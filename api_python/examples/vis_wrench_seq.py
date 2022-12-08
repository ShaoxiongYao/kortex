import sys
import os
import time
import numpy as np
import threading

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient

from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2

import matplotlib.pyplot as plt 

wrench_ary = np.load('wrench_ary_1670533286.npy')

plt.plot(wrench_ary[:, 0], label='f x')
plt.plot(wrench_ary[:, 1], label='f y')
plt.plot(wrench_ary[:, 2], label='f z')
plt.plot(wrench_ary[:, 3], label='tau x')
plt.plot(wrench_ary[:, 4], label='tau y')
plt.plot(wrench_ary[:, 5], label='tau z')
plt.legend()
plt.show()

