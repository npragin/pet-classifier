#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np
import tensorflow as tf
import tensorrt as trt

import pycuda.driver as cuda
import pycuda.autoinit

# For ONNX:

class ONNXClassifierWrapper():
    def __init__(self, file, num_classes, target_dtype = np.float32):
        
        self.target_dtype = target_dtype
        self.num_classes = num_classes
        self.load(file)
        
        self.stream = None
      
    def load(self, file):
        f = open(file, "rb")
        runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING)) 
        self.engine = runtime.deserialize_cuda_engine(f.read())
        self.context = self.engine.create_execution_context()

        
    def allocate_memory(self, batch):
        self.output = np.empty(self.num_classes, dtype = self.target_dtype) # Need to set both input and output precisions to FP16 to fully enable FP16

        # Allocate device memory
        self.d_input = cuda.mem_alloc(1 * batch.nbytes)
        self.d_output = cuda.mem_alloc(1 * self.output.nbytes)

        self.bindings = [int(self.d_input), int(self.d_output)]
        self.bindings_names = ["input", "output"]
        
        # Set binding addresses and shapes
        for i in range(2):  # We know we have 1 input and 1 output binding
            if i == 0:
                # For input tensor, set shape and address
                # self.context.set_input_shape(self.bindings_names[i], batch.shape)
                self.context.set_tensor_address(self.bindings_names[i], self.bindings[i])
            else:
                # For output tensor, just set the address
                self.context.set_tensor_address(self.bindings_names[i], self.bindings[i])

        # Verify all shapes are specified
        if not self.context.all_binding_shapes_specified:
            raise RuntimeError("Not all binding shapes are specified")

        self.stream = cuda.Stream()
        
    def predict(self, batch): # result gets copied into output
        if self.stream is None:
            self.allocate_memory(batch)
            
        # Convert PyTorch tensor to NumPy for debugging and GPU transfer
        batch_np = batch.detach().cpu().numpy()
            
        # Transfer input data to device
        cuda.memcpy_htod_async(self.d_input, batch_np, self.stream)
        # Execute model
        self.context.execute_async_v3(self.stream.handle)
        # Transfer predictions back
        cuda.memcpy_dtoh_async(self.output, self.d_output, self.stream)
        # Syncronize threads
        self.stream.synchronize()
        
        return self.output

def convert_onnx_to_engine(onnx_filename, engine_filename = None, max_batch_size = 32, max_workspace_size = 1 << 30, fp16_mode = True):
    logger = trt.Logger(trt.Logger.WARNING)
    with trt.Builder(logger) as builder, builder.create_network() as network, trt.OnnxParser(network, logger) as parser:
        builder.max_workspace_size = max_workspace_size
        builder.fp16_mode = fp16_mode
        builder.max_batch_size = max_batch_size

        print("Parsing ONNX file.")
        with open(onnx_filename, 'rb') as model:
            if not parser.parse(model.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))

        print("Building TensorRT engine. This may take a few minutes.")
        engine = builder.build_cuda_engine(network)

        if engine_filename:
            with open(engine_filename, 'wb') as f:
                f.write(engine.serialize())

        return engine, logger