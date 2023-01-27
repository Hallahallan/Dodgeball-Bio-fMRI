using System;
using UnityEngine;
using System.IO;

public class GameLogger : MonoBehaviour
{
    public int winner;
    public int playerBlueLives;
    public int playerPurpleLives;
    public string fileName;

    public void Start()
    {
        fileName = "GameLog_" + DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss") + ".txt";
    }
    public void LogGameInfo()
    {
        string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
        string logMessage = timestamp + ", Winner: " + winner + ", Blue lives left: " + playerBlueLives + ", Purple lives left: " + playerPurpleLives;
        // Create the "Logs" folder if it doesn't already exist
        string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs");
        
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(folderPath, fileName);
        File.AppendAllText(path, logMessage + Environment.NewLine);
    }
    private void OnApplicationQuit()
    {
        string logMessage = "Application Closed at: " + DateTime.Now.ToString();
        // Create the "Logs" folder if it doesn't already exist
        string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs");
        
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(Application.persistentDataPath, fileName);
        File.AppendAllText(path, logMessage + Environment.NewLine);
    }
}