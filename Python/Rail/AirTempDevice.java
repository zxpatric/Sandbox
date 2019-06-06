package tracker.testing;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import javax.comm.SerialPort;
import smx.tracker.TrackerException;
import java.io.PrintWriter;
import java.text.MessageFormat;
import java.util.Enumeration;
import javax.comm.CommPortIdentifier;
import smx.tracker.apps4xxx.utility.TrackerAppException;


public class AirTempDevice extends SerialDevice
{
    String checkErrCmd = "SYST:ERR?";
    String noErrResp = "0,\"No error\"";
    String deviceName = "HART,1560";
    private String comPortName = "";
    protected PrintWriter cmdWriter = null;
    protected BufferedReader cmdResponseReader = null;
    protected SerialPort sPort = null;
    
    private boolean found_device = false;

    public AirTempDevice(String deviceNameArg) throws TrackerException
    {
        found_device = detectDevice(9600, SerialPort.DATABITS_8, SerialPort.STOPBITS_1,SerialPort.PARITY_NONE, SerialPort.FLOWCONTROL_NONE,"*IDN?",deviceNameArg);
        if (found_device){
            deviceName = deviceNameArg;
            sendCommandNoWait("*CLS"); // clear all errors in the queue
        }
    }

    AirTempDevice() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    public boolean isDevicePresent(){
        return found_device;
    }
    
    protected void turnOnContinuousMeasurements() throws TrackerException
    {
        // The measurements get turn on the first time itself. In case if they
        // do
        // not we would like to try few more times instead of bailing out
        // immediately.
        // If the command to turn the measurements fails on blackstack, there is
        // no
        // point in running the procudure any further.

        boolean abortStabilityCheck = false;
        int MAX_RETRIES = 3;
        int retry_counter = 0;
        String val = null;

        do
        {
            sendDeviceCommand("INIT:CONT 1");
            val = sendDeviceCommand("INIT:CONT?");
            if (val.equals("1"))
            {
                break;
            }

            retry_counter++;
            if (retry_counter > 1)
            {
                System.out
                    .println(
                        "\t\tFailed to turn on measurements on Black Stack 1620 for Air Temp");
            }
        }
        while (retry_counter <= MAX_RETRIES && (null == val || val.equals(""))
               && false == abortStabilityCheck);

        if (val == null || val.equals(""))
        {
            throw new TrackerAppException(
                "Failed to turn on continuous measurements on BlackStack 1620. Please make sure the device is properly plugged in.");
        }
    }

    public String sendDeviceCommand(String cmd) throws TrackerException
    {
        String cmdResp = sendCommand(cmd); // turn echo off
        String errResp = sendCommand(checkErrCmd);
        if (!errResp.equals(noErrResp))
        {
            throw new TrackerAppException("Error when executing command \""
                                          + cmd + "\" on BlackStack 1620. Err:" +
                                          errResp);
        }
        return cmdResp;
    }

    public double getTemperature1() throws TrackerException
    {
        int MAX_RETRIES = 20;
        double temp = 0;
        String resp = "";
        String statResp = "";

        for (int i = 0; i < MAX_RETRIES; i++)
        {
            // This query command reads the Operation Status Condition Register
            // The response 16 would be given if a new measurement was acquired
            // since the last time this command was issued
            statResp = sendDeviceCommand("STAT:OPER?");

            if (statResp != null && statResp.equals("16"))
            {
                resp = sendDeviceCommand("FETC?(@1)");
                if (resp != null && !resp.equals(""))
                {
                    break;
                }
            }
            try
            {
                Thread.sleep(100);
            }
            catch (InterruptedException ex)
            {
            }
        }

        if (statResp == null || !statResp.equals("16"))
        {
            throw new TrackerAppException(
                "Failed to start measurements on BlackStack 1620 to get Air Temp. Please make sure the device is properly plugged in");
        }

        if (resp == null || resp.equals(""))
        {
            throw new TrackerAppException(
                "Failed to get Air Temp. Please make sure the device is properly plugged in");
        }

        // if (resp.equals("16"))
        {
            // resp = sendDeviceCommand("FETC?(@1)");
            temp = Double.parseDouble(resp);
        }
        return temp;

    }

    private boolean waitForNewMeasurement() throws TrackerException
    {
        String resp = sendCommand("STAT:OPER?");
        if (resp.equals("16"))
        {
            return true;
        }
        else
        {
        }
        return false;
    }

    double getTemperature() throws TrackerException
    {
        boolean abortStabilityCheck = false;
        int MAX_RETRIES = 3;
        int sensorNumber = 1;
        int retry_counter = 0;
        String val = null;
        do
        {
            val = sendCommand("meas? (@" + sensorNumber + ")");
            retry_counter++;
            if (retry_counter > 1)
            {
                System.out.println("\t\tRetrying temp" + "(" + retry_counter+ "): " + val);
            }
        }
        while (retry_counter <= MAX_RETRIES && (null == val || val.equals(""))
               && false == abortStabilityCheck);


        double temp = Double.parseDouble(val);
        return temp;
    }

    void closeDevice()
    {
        closePort();
    }
    
}
