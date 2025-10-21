# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.programmablePsu.python.programmablePsu.v1.programmablePsu_pb2 as Pb


class Client(ClientConnection):
    """
    programmablePsu functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        super().__init__(FbClient(
            "_io4edge_colorLED._tcp", addr, command_timeout, connect=connect
        ))

    @connectable
    def set_calibration(self, calib: Pb.CalibrationValues):
        """
        Upload the calibration to the programmable PSU.
        calib contains values for 
        * PSU control: dac_voffs, dac_vgain, dac_coffs, dac_cgain.
        * ADC measurement: adc_vout_offs, adc_vout_gain, adc_vsense_offs, adc_vsense_gain, adc_coffs, adc_cgain.
        * Calibration date
        The calibration values are saved persistent in the device and are applied immediately.
        @param calib: calibration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.ConfigurationSet()
        fs_cmd.calibration_values.CopyFrom(calib)
        self._client.upload_configuration(fs_cmd)

    @connectable
    def set_recovery_mode(self, auto_recover: bool):
        """
        Set the recovery mode of the programmable PSU.
        The recovery mode is not persistent and is reset on power cycle.
        @param auto_recover: if true the auto recovery mode shall be enabled
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setRecoveryMode.auto_recover = auto_recover
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def get_calibration(self) -> Pb.CalibrationValues:
        """
        Download the calibration from the programmable PSU.
        @return: actual calibration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response.calibration_values

    @connectable
    def get_recovery_mode(self) -> bool:
        """
        Download the recovery mode from the programmable PSU.
        @return: actual recovery mode
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(Pb.FunctionControlGet(), fs_response)
        return fs_response.getRecoveryMode.auto_recover

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the programmable PSU.
        The description includes information about the maximum voltage, current, and power.
        @return: description from the programmable PSU 
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set_voltage_level(self, level: float):
        """
        Set the voltage level of the programmable PSU.
        @param level: voltage level to set (in Volts)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setVoltageLevel.level = level
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def set_output_enabled(self, enabled: bool):
        """
        Set the output enabled state of the programmable PSU.
        @param enabled: if true the output is enabled
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setOutputEnabled.enabled = enabled
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def set_current_limit(self, limit: float):
        """
        Set the current limit of the programmable PSU.
        @param limit: current limit to set (in Amperes)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setCurrentLimit.limit = limit
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())


    @connectable
    def get_state(self) -> Pb.FunctionControlGetResponse:
        """
        Get the state of the programmable PSU.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response
