import tensorflow as tf

with tf.name_scope("Inference"):  # 输出
    x = tf.Variable(tf.truncated_normal(shape=[1, 2], mean=0, stddev=1000))
    f = tf.matmul(a=x, b=x, transpose_a=False, transpose_b=True)

with tf.name_scope("Loss"): #损失
    loss = f

with tf.name_scope("Train"):#训练
    train = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(f)

sess = tf.Session() #会话
sess.run(tf.global_variables_initializer()) #变量初始化

iteration = 50
for step in range(iteration):
    sess.run(train)
    print(sess.run(x))
