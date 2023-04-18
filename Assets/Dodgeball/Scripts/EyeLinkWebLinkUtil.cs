using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using System.IO;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Linq;


public class EyeLinkWebLinkUtil : MonoBehaviour
{
	//[MenuItem("Tools/Write file")]
	//public static StreamWriter writer;
	//[Screen.fullScreen][1] = true;
	//public static string path = "Assets/myIAS.ias";
	public static string path = "AgentIASxb.ias";
	//public static StreamWriter writer = new StreamWriter(openIASFile.path, true);
	public static StreamWriter writer = File.CreateText(EyeLinkWebLinkUtil.path);
	//using (StreamWriter writer = new StreamWriter(openIASFile.path, true));
	public static int iasZeroPoint;


	// start MJ added for UDP

	public static int localPort;

	// prefs
	public static string IP;  // define in init
	public static int portForSending;  // define in init
	public static int portForReceiving; // define in init
	// "connection" things
	public static IPEndPoint remoteEndPointForSending;
	public static IPEndPoint remoteEndPointForReceiving;
	public static UdpClient client;
	public static UdpClient udpServer;
	public static byte[] receivedData;
	public static int screenResX = 1920;
	public static int screenResY = 1080;
	public static float eyeX = 0.0F;
	public static float eyeY = 0.0F;
	public static float eyePupil = 0.0F;
	public static int timeOffset = 133;

	//string strMessage = "!V IAREA FILE myIASxb.ias";


	[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
	public static void openFileToWrite()
    {


		print("UDPSend.init()");
		IP = "127.0.0.1";
		portForSending = 3467;
		portForReceiving = 3468;

		// setup for port sending
		remoteEndPointForSending = new IPEndPoint(IPAddress.Parse(IP), portForSending);
		remoteEndPointForReceiving = new IPEndPoint(IPAddress.Parse(IP), portForReceiving);
		client = new UdpClient();
		udpServer = new UdpClient(portForReceiving);
		udpServer.Client.ReceiveTimeout = 3;

		

		Debug.Log("I am alive!");

		// set up test message to send
		byte[] data = Encoding.UTF8.GetBytes("MJ UPD Test");


		// send test message		
		client.Send(data, data.Length, remoteEndPointForSending);


		iasZeroPoint = Convert.ToInt32(Time.realtimeSinceStartup * 1000);
		// send message indicating the name of the IAS file
		// the time of the message is the 0 time point point for IAS file (for any dynamic interest area times)
		data = Encoding.UTF8.GetBytes("!V IAREA FILE myIASxb.ias");

		// send the messages
		client.Send(data, data.Length, remoteEndPointForSending);

	}


	public static Rect getScreenRectFromGameObject(GameObject gameObject)
	{

		Vector3 cen = gameObject.GetComponent<Renderer>().bounds.center;
		Vector3 ext = gameObject.GetComponent<Renderer>().bounds.extents;
		Vector2[] extentPoints = new Vector2[8]
		{
			Camera.main.WorldToScreenPoint(new Vector3(cen.x-ext.x, cen.y-ext.y, cen.z+ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x+ext.x, cen.y-ext.y, cen.z+ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x-ext.x, cen.y-ext.y, cen.z-ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x+ext.x, cen.y-ext.y, cen.z-ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x-ext.x, cen.y+ext.y, cen.z+ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x+ext.x, cen.y+ext.y, cen.z+ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x-ext.x, cen.y+ext.y, cen.z-ext.z)),
			Camera.main.WorldToScreenPoint(new Vector3(cen.x+ext.x, cen.y+ext.y, cen.z-ext.z))
		};
		Vector2 min = extentPoints[0];
		Vector2 max = extentPoints[0];
		foreach (Vector2 v in extentPoints)
		{
			min = Vector2.Min(min, v);
			max = Vector2.Max(max, v);
		}

		//set left/right/top/bottom in EyeLink coords (0,0 top left rather than Unity's 0,0 bottom left)
		float left = min.x;
		float top = screenResY - max.y;
		float right = max.x;
		float bottom = screenResY - min.y;

		return new Rect((int)Math.Round(left), (int)Math.Round(top), (int)Math.Round(right - left), (int)Math.Round(bottom - top));
	}

	public static List<float> getSampleData()
	{
		
		receivedData = udpServer.Receive(ref remoteEndPointForReceiving);
		
		string sampleString = Encoding.UTF8.GetString(receivedData);
		//string ttW = "sampleString  = " + sampleString;
		//EyeLinkWebLinkUtil.writeIASLine(ttW);
		List<string> sampleList = sampleString.Split().ToList();

		if (sampleList[0] == "Sample")
		{

			if (sampleList[2] == "Both")
			{

				float leftX = float.Parse(sampleList[3]);

				float leftY = float.Parse(sampleList[4]);
				float leftPupil = float.Parse(sampleList[5]);
				float rightX = float.Parse(sampleList[6]);
				float rightY = float.Parse(sampleList[7]);
				float rightPupil = float.Parse(sampleList[8]);

				eyeX = rightX;
				eyeY = rightY;
				eyePupil = rightPupil;
				//Debug.Log("Eye data  = " + eyeX + "  " + eyeY + "  " + eyePupil);
			}
			else
			{
				eyeX = float.Parse(sampleList[3]);
				eyeY = float.Parse(sampleList[4]);
				eyePupil = float.Parse(sampleList[3]);
			}
			var eyeData = new List<float> { eyeX, eyeY, eyePupil };

			return eyeData;
		}

		else 
		{
			return new List<float>();
		}

	}

	public static void writeIASLine(string textToWrite)
	{
		writer.WriteLine(textToWrite);
	}


	public static void sendString(string message)
	{
		try
		{
			if (message != "")
			{

			// use utf8 encoding to set up message
			byte[] data = Encoding.UTF8.GetBytes(message);

			// send the message
			client.Send(data, data.Length, remoteEndPointForSending);
			}
		}
		catch (Exception err)
		{
			print(err.ToString());
		}
	}


}
