import numpy as np
import tensorflow as tf
import tflearn
from tensorflow.keras.layers import BatchNormalization

weight_regularizer = tf.keras.regularizers.l2(0.0005)

# for reuse 

def uniform(shape, scale=0.05, name=None):
	"""Uniform init."""
	initial = tf.random.uniform(shape, minval=-scale, maxval=scale, dtype=tf.float32)
	return tf.compat.v1.get_variable(name, shape=shape, initializer = tf.initializer.random_uniform(minval=-scale, maxval = scale), dtype=tf.float32)


def glorot(shape, name=None):
	"""Glorot & Bengio (AISTATS 2010) init."""
	return tf.compat.v1.get_variable(name, shape = shape, initializer = tf.compat.v1.glorot_uniform_initializer(), dtype=tf.float32)


def zeros(shape, name=None):
	"""All zeros."""
	initial = tf.zeros(shape, dtype=tf.float32)
	return tf.compat.v1.get_variable(name, shape=shape, initializer=tf.compat.v1.constant_initializer(0.0), dtype=tf.float32)


def ones(shape, name=None):
	"""All ones."""
	initial = tf.ones(shape, dtype=tf.float32)
	return tf.compat.v1.get_variable(name, shape=shape, initializer=tf.compat.v1.constant_initializer(1.0), dtype=tf.float32)

def dot(x, y, sparse=False):
	"""Wrapper for tf.matmul (sparse vs dense)."""
	if sparse:
		res = tf.sparse.sparse_dense_matmul(x, y)
	else:
		res = tf.matmul(x, y)
	return res



def create_conv_layer(name, input_tensor, in_channels, out_channels, is_training = True, activation='relu', kx = 3, ky = 3, stride_x = 2, stride_y = 2, batchnorm=False, padding='VALID', add=None, deconv = False):
	if deconv == False:
		input_tensor = tf.pad(input_tensor, [[0, 0], [int(kx/2), int(kx/2)], [int(kx/2), int(kx/2)], [0, 0]], mode="CONSTANT")


	weights = tf.compat.v1.get_variable(name+'weights', shape=[kx, ky, in_channels, out_channels],
			initializer=tf.compat.v1.truncated_normal_initializer(stddev=np.sqrt(0.02 / kx / ky / in_channels)),
			regularizer=weight_regularizer,
			dtype=tf.float32
	)
	biases = tf.compat.v1.get_variable(name+'biases', shape=[out_channels], initializer=tf.compat.v1.constant_initializer(0.0),regularizer=weight_regularizer, dtype=tf.float32)

	

	if deconv == False:
		t = tf.nn.conv2d(input_tensor, filters=weights, strides=[1, stride_x, stride_y, 1], padding=padding)
		s = tf.nn.bias_add(t, biases)

	else:
		batch = tf.shape(input_tensor)[0]
		size = tf.shape(input_tensor)[1]

		t = tf.nn.conv2d_transpose(input_tensor, tf.transpose(weights,perm=[0,1,3,2]),[batch, size * stride_x, size * stride_y, out_channels], [1, stride_x, stride_y, 1],
				padding='SAME', data_format = "NHWC")

		s = tf.nn.bias_add(t, biases)

	if add is not None: # res
		s = s + add 

	if batchnorm:

                n = BatchNormalization(momentum = 0.99, center=True, scale=True)(s)

	else:
		n = s 

	if activation == 'relu':
			return tf.nn.relu(n), weights, biases
	elif activation == 'sigmoid':
			return tf.nn.sigmoid(n), weights, biases
	elif activation == 'tanh':
			return tf.nn.tanh(n), weights, biases
	elif activation == 'linear':
			return n, weights, biases

