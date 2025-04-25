from onnx_helper import ONNXClassifierWrapper
import tensorrt as trt
import time
import torch
import numpy as np

def main():
    model = ONNXClassifierWrapper("breed_classifier.trt", num_classes=37, target_dtype=np.float16)

    while input("Enter 'q' to quit, anything else to continue: ") != 'q':
        dummy_input_batch = torch.rand(1, 3, 224, 224)
        t = time.time()
        out = model.predict(dummy_input_batch)
        t = time.time() - t
        print(np.argmax(out))
        print(f"Time taken: {t} seconds")




if __name__ == "__main__":
    main()