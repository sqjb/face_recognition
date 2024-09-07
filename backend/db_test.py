import numpy as np
import time
import random
import string

# 模拟 Representation 类
class Representation:
    def __init__(self, person_name, file_name, timestamp, descriptor):
        self.person_name = person_name
        self.file_name = file_name
        self.timestamp = timestamp
        self.descriptor = descriptor

# 生成随机人脸特征
def generate_random_representations(num_reps):
    reps = []
    for _ in range(num_reps):
        person_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        file_name = f"{person_name}_image.jpg"
        timestamp = int(time.time())
        descriptor = np.random.rand(128)  # dlib 默认的 face_recognition_model_v1 使用 128 维的特征描述符
        rep = Representation(person_name, file_name, timestamp, descriptor)
        reps.append(rep)
    return reps

# 生成测试人脸特征
def generate_test_descriptor():
    return np.random.rand(128)

def compare_faces(known_reps, test_descriptor):
    start_time = time.time()
    distances = []
    for rep in known_reps:
        distance = np.linalg.norm(rep.descriptor - test_descriptor)
        distances.append(distance)
    min_distance = min(distances)
    end_time = time.time()
    return min_distance, end_time - start_time

if __name__ == '__main__':
    # 1. 生成随机人脸特征数据
    print("Generating random face representations...")
    known_reps = generate_random_representations(20000)
    print(f"Generated {len(known_reps)} face representations.")
    
    # 2. 生成测试人脸特征
    print("Generating test face descriptor...")
    test_descriptor = generate_test_descriptor()
    
    # 3. 比对人脸特征
    print("Comparing faces...")
    min_distance, comparison_time = compare_faces(known_reps, test_descriptor)
    
    # 4. 输出结果
    print(f"Minimum distance: {min_distance:.4f}")
    print(f"Time taken for face comparison: {comparison_time:.4f} seconds")
    
    # 5. 检查内存使用情况（可选）
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"Memory usage: {mem_info.rss / 1024**2:.2f} MB")
