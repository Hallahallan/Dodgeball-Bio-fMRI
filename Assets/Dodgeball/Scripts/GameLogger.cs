using System;
using UnityEngine;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Content;
using UnityEngine.Serialization;

public class GameLogger : MonoBehaviour
{
    
    public DodgeBallGameController gameController;
    
    public int winner;
    public int blueLives;
    public int purpleLives;
    public int blueBalls;
    private int _latestBlueBalls = 0;
    private int _latestBlueLives = 3;
    private int _latestPurpleLives = 3;
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
    
    // // Log when the application is closed
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
            // Write column names if the file is empty
            if (new FileInfo(path).Length == 0)
            {
                writer.WriteLine("Timestamp,EventType,BallsLeft,PlayerLives,EnemyLives");
                writer.WriteLine($"{timestamp},{"Init"},{0},{3},{3}");

            }
            
            string eventType = "";
            switch (n)
            {
                case 1:
                    eventType = "PlayerThrewBall";
                    break;
                case 2:
                    eventType = "PickedUpBall";
                    break;
                case 3:
                    eventType = "HitEnemy";
                    break;
                case 4:
                    eventType = "TookDamage";
                    break;
                case 5:
                    eventType = "EnemyThrewBall";
                    break;
            }

            // Update all the latest values every time
            _latestBlueBalls = gameController.Team0Players[0].Agent.currentNumberOfBalls;
            _latestBlueLives = gameController.Team0Players[0].Agent.HitPointsRemaining;
            _latestPurpleLives = gameController.Team1Players[0].Agent.HitPointsRemaining;
            // _latestCornerStatus = gameController.Team1Players[1].Agent.IsInCorner; // Add for enemy in corner, remember to add to writer.Writelines both here and above

            writer.WriteLine($"{timestamp},{eventType},{_latestBlueBalls},{_latestBlueLives},{_latestPurpleLives}");
        }
    }
}