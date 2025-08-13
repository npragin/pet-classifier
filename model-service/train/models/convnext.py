import torch
from torch import Tensor
import torch.nn as nn
import torch.nn.functional as F


class LayerNorm2d(nn.Module):
    def __init__(self, in_channels):
      super().__init__()
      self.layer_norm = nn.LayerNorm(in_channels)

    def forward(self, x: Tensor) -> Tensor:
      x = x.permute((0,2,3,1))
      x = self.layer_norm(x)
      return x.permute((0,3,1,2))

class ConvNextStem(nn.Module):
   def __init__(self, in_channels, out_channels, kernel_size=3):
    super().__init__()
    self.patchify = nn.Conv2d(in_channels, out_channels, kernel_size, stride=kernel_size)
    self.layer_norm = LayerNorm2d(out_channels)
  
   def forward(self,x):
     x = self.patchify(x)
     return self.layer_norm(x)
    

class ConvNextBlock(nn.Module):

  def __init__(self, d_in, layer_scale=1e-6, kernel_size=7, stochastic_depth_prob=1):
    super().__init__()
    self._stochastic_depth_prob = stochastic_depth_prob

    self.conv1 = nn.Conv2d(d_in, d_in, kernel_size, padding="same", groups=d_in)
    self.layer_norm = LayerNorm2d(d_in)
    self.conv2 = nn.Conv2d(d_in, 4 * d_in, 1)
    self.conv3 = nn.Conv2d(4 * d_in, d_in, 1)
    self.layer_scale = nn.Parameter(torch.ones((1, d_in, 1, 1)) * layer_scale)


  def forward(self,x):
    # if self.training and torch.rand(1) > self._stochastic_depth_prob:
    #   return x

    identity = x

    x = self.conv1(x)
    x = self.layer_norm(x)
    x = self.conv2(x)
    x = F.gelu(x)
    x = self.conv3(x)
    x = x * self.layer_scale + identity

    return x

class ConvNextDownsample(nn.Module):
  def __init__(self, d_in, d_out, width=2):
    super().__init__()
    self.layer_norm = LayerNorm2d(d_in)
    self.downsample = nn.Conv2d(d_in, d_out, kernel_size=width, stride=width)

  def forward(self,x):
    x = self.layer_norm(x)
    x = self.downsample(x)

    return x

class ConvNextClassifier(nn.Module):
  def __init__(self, d_in, d_out):
    super().__init__()
    self.layer_norm = nn.LayerNorm(d_in)
    self.linear = nn.Linear(d_in, d_out)

  def forward(self,x):
    x = F.avg_pool2d(x, x.size()[2:]).squeeze(-1).squeeze(-1)
    x = self.layer_norm(x)
    x = self.linear(x)
    
    return x


class ConvNext(nn.Module):
  """
  Note: On instantiation, blocks should be a list where each element is the number of
        output channels of the residual blocks. A downsampling layer will be inserted
        wherever the channel dimensionality changes.
  """

  def __init__(self, in_channels, out_channels, blocks=[96]):
    super().__init__()

    stochastic_depth = lambda l: 1 - (l / len(blocks)) * 0.5

    self.network = nn.Sequential()
    self.network.append(ConvNextStem(in_channels, blocks[0]))

    for i, c in enumerate(blocks):
      if i > 0 and blocks[i - 1] != c:
        self.network.append(ConvNextDownsample(blocks[i - 1], c))
      self.network.append(ConvNextBlock(c, stochastic_depth_prob=stochastic_depth(i + 1)))

    self.network.append(ConvNextClassifier(blocks[-1], out_channels))


    for m in self.modules():
      if isinstance(m, (nn.Conv2d, nn.Linear)):
        nn.init.trunc_normal_(m.weight, std=0.02)
        nn.init.constant_(m.bias, 0)
      elif isinstance(m, nn.LayerNorm):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)

  def forward(self,x):
    return self.network(x)
