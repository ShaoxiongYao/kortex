#! /usr/bin/env python3

###
# KINOVA (R) KORTEX (TM)
#
# Copyright (c) 2018 Kinova inc. All rights reserved.
#
# This software may be modified and distributed
# under the terms of the BSD 3-Clause license.
#
# Refer to the LICENSE file for details.
#
###

import sys
import os
import time
import numpy as np
import threading

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient

from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2

import matplotlib.pyplot as plt 

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 20

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications

    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

def SendCallWithRetry(call, retry,  *args):
    i = 0
    arg_out = []
    while i < retry:
        try:
            arg_out = call(*args)
            break
        except:
            i = i + 1
            continue
    if i == retry:
        print("Failed to communicate")
    return arg_out

class PlotSeq:
    def __init__(self, vis_steps, val_range, prefix):
        self.vis_steps = vis_steps
        self.val_range = val_range
        plt.axis([0, vis_steps, val_range[0], val_range[1]])
        plt.ion()
        plt.show(block=False)
        self.prefix = prefix
    
    def update_seq(self, np_seq, fig_fn=None, block=False):
        seq_len, n_lines = np_seq.shape
        for idx in range(n_lines):
            st_idx = max(0, seq_len - self.vis_steps)
            line_data = np_seq[st_idx:, idx]
            plt.plot(line_data, label=" ".join([self.prefix, str(idx)]))

        plt.ylim(self.val_range)
        plt.xlabel("time step")
        plt.ylabel(self.prefix)
        plt.legend()
        plt.draw()
        if block:
            plt.show()
        else:
            plt.pause(0.01)
        if fig_fn is not None:
            plt.savefig(fig_fn)
        plt.clf()

def main():
    
    # Import the utilities helper module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parse arguments
    args = utilities.parseConnectionArguments()

    plotter = PlotSeq(vis_steps=100, val_range=[-10, 10], prefix='wrench dim')

    wrench_ary = np.zeros((0, 6))

    tot_num_steps = 3000
    
    start_time = time.time()
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:

        with utilities.DeviceConnection.createUdpConnection(args) as router_real_time:

            # Create required services
            base = BaseClient(router)
            base_cyclic = BaseCyclicClient(router_real_time)

            for _ in range(tot_num_steps):
                base_feedback = BaseCyclic_pb2.Feedback()
                base_feedback = SendCallWithRetry(base_cyclic.RefreshFeedback, 3)
                
                # print("base_feedback:", base_feedback)

                f_x = base_feedback.base.tool_external_wrench_force_x
                f_y = base_feedback.base.tool_external_wrench_force_y
                f_z = base_feedback.base.tool_external_wrench_force_z

                tau_x = base_feedback.base.tool_external_wrench_torque_x
                tau_y = base_feedback.base.tool_external_wrench_torque_y
                tau_z = base_feedback.base.tool_external_wrench_torque_z

                f_vec = np.array([[f_x, f_y, f_z, tau_x, tau_y, tau_z]])
                wrench_ary = np.append(wrench_ary, f_vec, axis=0)

                plotter.update_seq(wrench_ary)

    print("collection time:", time.time()-start_time)

    wrench_fn = f'wrench_ary_{int(time.time())}.npy'
    np.save(wrench_fn, wrench_ary)

    # plt.plot(wrench_ary[:, 0], label='f x')
    # plt.plot(wrench_ary[:, 1], label='f y')
    # plt.plot(wrench_ary[:, 2], label='f z')
    # plt.legend()
    # plt.show()



if __name__ == "__main__":
    exit(main())
