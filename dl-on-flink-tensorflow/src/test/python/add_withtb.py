#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import tensorflow as tf
import sys
import time
from tensorflow.python.summary.writer.writer_cache import FileWriterCache as SummaryWriterCache
from dl_on_flink_tensorflow.tensorflow_context import *


def build_graph():
    global a
    a = tf.placeholder(tf.float32, shape=None, name="a")
    b = tf.reduce_mean(a, name="b")
    r_list = []
    for i in range(1):
        v = tf.Variable(dtype=tf.float32, initial_value=tf.constant(1.0), name="v_" + str(i))
        c = tf.add(b, v, name="c_" + str(i))
        add = tf.assign(v, c, name="assign_" + str(i))
        sum = tf.summary.scalar(name="sum_" + str(i), tensor=c)
        r_list.append(add)

    global_step = tf.contrib.framework.get_or_create_global_step()
    global_step_inc = tf.assign_add(global_step, 1)
    r_list.append(global_step_inc)
    return r_list


def map_func(context):
    tf_context = TFContext(context)
    job_name = tf_context.get_role_name()
    index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster()
    print (cluster_json)
    sys.stdout.flush()
    ckpt = tf_context.get_property("checkpoint_dir")
    cluster = tf.train.ClusterSpec(cluster=cluster_json)
    server = tf.train.Server(cluster, job_name=job_name, task_index=index)
    sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False,
                                 device_filters=["/job:ps", "/job:worker/task:%d" % index])
    t = time.time()
    if 'ps' == job_name:
        from time import sleep
        while True:
            sleep(1)
    else:
        with tf.device(tf.train.replica_device_setter(worker_device='/job:worker/task:' + str(index), cluster=cluster)):
            train_ops = build_graph()
            try:
                hooks = [tf.train.StopAtStepHook(last_step=50)]
                with tf.train.MonitoredTrainingSession(master=server.target, config=sess_config,
                                                       checkpoint_dir=ckpt, hooks=hooks,
                                                       save_summaries_steps=1) as mon_sess:
                    while not mon_sess.should_stop():
                        print (mon_sess.run(train_ops, feed_dict={a: [1.0, 2.0, 3.0]}))
                        sys.stdout.flush()
                        time.sleep(1)
            finally:
                SummaryWriterCache.clear()


if __name__ == "__main__":
    map_func(context)
