import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as BinIoPb
import google.protobuf.any_pb2 as AnyPb

fs_msg = BinIoPb.ConfigurationSet()
fs_msg.changeOutputWatchdog = True
fs_msg.outputWatchdogTimeout = 1000
fs_msg.outputWatchdogMask = 0x01

fs_any = AnyPb.Any()
fs_any.Pack(fs_msg)

m = FbPb.Command()
m.context.value = "abc"
m.Configuration.functionSpecificConfigurationSet.CopyFrom(fs_any)

s = m.SerializeToString()
print(m)

m2 = FbPb.Command()
m2.ParseFromString(s)
print("M2 is", m2)

fs_any2 = AnyPb.Any()
fs_any2.CopyFrom(m2.Configuration.functionSpecificConfigurationSet)
fs_any2.type_url = ""

fs_msg2 = BinIoPb.ConfigurationSet()
fs_any2.Unpack(fs_msg2)

print("fs_any2 is", fs_any2)
print("fs_msg2 is", fs_msg2)
