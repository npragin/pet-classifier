import tensorrt as trt
import os

def build_engine_from_onnx(onnx_file_path, engine_file_path, precision_mode="fp32"):
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    config = builder.create_builder_config()
    config.set_flag(trt.BuilderFlag.FP16)

    parser = trt.OnnxParser(network, logger)
    
    with open(onnx_file_path, 'rb') as model:
        if not parser.parse(model.read()):
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return False
    
    engine = builder.build_serialized_network(network, config)
    
    with open(engine_file_path, 'wb') as f:
        f.write(engine)

    return True


if __name__ == "__main__":
    onnx_model = "breed_classifier.onnx"
    engine_file = "breed_classifier.trt"
    build_engine_from_onnx(onnx_model, engine_file)