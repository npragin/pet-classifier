import argparse
import os

import torch
import torch.nn as nn

from models.convnext import ConvNext
from train import evaluate, config, device
from datasets.cifar10 import getCIFAR10Dataloaders

def load_model_from_chkpt(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    try:
        checkpoint = torch.load(filename)
        model = ConvNext(3, 10, checkpoint["blocks"])
        model.load_state_dict(checkpoint["state_dict"])
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise
    
    return model

def main():
    parser = argparse.ArgumentParser(description="Evaluate a model checkpoint on CIFAR test")
    parser.add_argument("filename", type=str, help="Location of model checkpoint")
    args = parser.parse_args()

    model = load_model_from_chkpt(args.filename)
    model.compile()
    model.to(device)

    _, _, test_loader = getCIFAR10Dataloaders(config)

    test_loss, test_acc = evaluate(model, test_loader)

    print(f"Average test loss: {test_loss}\nAverage test accuracy: {test_acc}")



if __name__ == "__main__":
    main()