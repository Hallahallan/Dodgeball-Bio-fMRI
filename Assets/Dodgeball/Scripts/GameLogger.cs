using System;
using UnityEngine;
using System.IO;
using UnityEditor;
using UnityEngine.Serialization;

public class GameLogger : MonoBehaviour
{
    public int winner;
    public int blueLives;
    public int purpleLives;
    public int blueBalls;
    public int hit;
    public int thrower;
    public string fileNameResults;
    public string fileNamePlayerData;
    public string winstr;

    public void Start()
    {
        fileNameResults = "GameLog_Results_" + DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss") + ".txt";
        fileNamePlayerData = "GameLog_Player_Data_" + DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss") + ".txt";
    }
    public void LogGameInfo()
    {
        string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
        
        // Change winner to blue and purple instead of 0 and 1
        if (winner == 0) { winstr = "Blue"; }
        else if (winner == 1) { winstr = "Purple"; }  
        else { winstr = "Draw"; }
        
        string logMessage = "Time: " + timestamp + ", Winner: " + winstr + ", Blue lives left: " + blueLives + ", Purple lives left: " + purpleLives;
        // Create the "Logs" folder if it doesn't already exist
        string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs/Results");
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(folderPath, fileNameResults);
        using (StreamWriter writer = File.AppendText(path))
        {
            writer.WriteLine(logMessage);
        }
    }
    // private void OnApplicationQuit()
    // {
    //     string logMessage = "Application Closed at: " + DateTime.Now.ToString();
    //     // Create the "Logs" folder if it doesn't already exist
    //     string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs/Results");
    //     if (!Directory.Exists(folderPath))
    //     {
    //         Directory.CreateDirectory(folderPath);
    //     }
    //     string path = Path.Combine(folderPath, fileNameResults);
    //     File.AppendAllText(path, logMessage + Environment.NewLine);
    // }

    public void LogPlayerData(int n)
    {
        
        string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
        string folderPath = Path.Combine(Application.dataPath, "DodgeBall/Logs/PlayerData"); //Creates folder path
        //If folder path doesn't exist, create it
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(folderPath, fileNamePlayerData);
        
        using (StreamWriter writer = File.AppendText(path))
        {
            switch(n)
            {
                //Player shoots
                case 1:
                    writer.WriteLine("Threw ball at: " + timestamp + ", Balls left: " + blueBalls);
                    break;
                //Player picks up ball
                case 2:
                    writer.WriteLine("Picked up ball at: " + timestamp + ", Balls left: " + blueBalls);
                    break;
                //Player takes damage
                case 3:
                    writer.WriteLine("Hit enemy at: " + timestamp + ", Enemy lives left " + purpleLives);
                    break;
                //Player deals damage
                case 4:
                    writer.WriteLine("Took damage at: " + timestamp + ", Player lives left " + blueLives);
                    break;
            }
        }
    }
}