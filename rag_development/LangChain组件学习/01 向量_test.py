import numpy

def get_dot(vec_a,vec_b):
    """
    计算两个向量的点积
    :param vec_a: 向量a
    :param vec_b: 向量b
    :return: a，b的点积
    """
    if len(vec_a) != len(vec_b):
        print("两个向量的维度不一致")
        return None
    return numpy.dot(vec_a,vec_b)

def get_norm( vec):
    """
    计算单个向量的模长
    :param vec: 向量
    :return: 模长
    """
    return numpy.linalg.norm(vec)

def get_cos(vec_a,vec_b):
    """
    计算两个向量的余弦相似度
    :param vec_a: 向量a
    :param vec_b: 向量b
    :return: a，b的余弦相似度
    """
    if len(vec_a) != len(vec_b):
        print("两个向量的维度不一致")
        return None
    return get_dot(vec_a,vec_b)/(get_norm(vec_a)*get_norm(vec_b))

if __name__ == '__main__':
    vec_a = numpy.array([1,2,3])
    vec_b = numpy.array([2,3,4])
    print(get_cos(vec_a,vec_b))