from warnings import warn

try:
    from rpi_rf import RFDevice
except RuntimeError as err:
    warn('\n\n'.join(err.args))
    RFDevice = None


class SingleRFDeviceMeta(type):

    instances = {}

    def __call__(mcs, gpio, *args, **kwargs):
        if gpio not in mcs.instances:
            mcs.instances[gpio] = super().__call__(gpio, *args, **kwargs)
        return mcs.instances[gpio]

if RFDevice:
    class SingleRFDevice(RFDevice, metaclass=SingleRFDeviceMeta):
        pass
else:
    from unittest.mock import MagicMock
    SingleRFDevice = MagicMock()
