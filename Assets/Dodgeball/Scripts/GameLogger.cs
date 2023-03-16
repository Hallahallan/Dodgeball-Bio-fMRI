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
    public string fileNameResults;
    public string fileNamePlayerData;

    public void Start()
    {
        fileNameResults = "GameLog_Results_" + DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss") + ".txt";
        fileNamePlayerData = "GameLog_Player_Data_" + DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss") + ".txt";
    }
    public void LogGameInfo()
    {
        //TODO: Hvorfor logges ikke data??????
        Debug.Log("Kristian er kek");
        string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
        string logMessage = timestamp + ", Winner: " + winner + ", Blue lives left: " + blueLives + ", Purple lives left: " + purpleLives;
        // Create the "Logs" folder if it doesn't already exist
        string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs/Results");

        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(folderPath, fileNameResults);
        File.AppendAllText(path, logMessage + Environment.NewLine);
    }
    private void OnApplicationQuit()
    {
        string logMessage = "Application Closed at: " + DateTime.Now.ToString();
        // Create the "Logs" folder if it doesn't already exist
        string folderPath = Path.Combine(Application.dataPath, "Dodgeball/Logs/Results");
        
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(Application.persistentDataPath, fileNameResults);
        File.AppendAllText(path, logMessage + Environment.NewLine);
    }

    public void LogPlayerData(int n)
    {
        /***
         * Data to log:
         * When the player shoots
         * When the player picks up a ball
         * How many balls the player has when either of these occur
         * If the player hits the enemy
         * If the player gets hit
         * How many lives each player has when either of these occur
         */
        string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
        string folderPath = Path.Combine(Application.dataPath, "DodgeBall/Logs/PlayerData"); //Creates folder path
        //If folder path doesn't exist, create it
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        string path = Path.Combine(Application.persistentDataPath, fileNamePlayerData);
        switch(n)
        {
            //Player shoots
            case 1:
                File.AppendAllText(path, timestamp + "Throw" + Environment.NewLine);
                File.AppendAllText(path, timestamp + blueBalls + Environment.NewLine);
                break;
            //Player picks up ball
            case 2:
                File.AppendAllText(path, timestamp + "Pickup" + Environment.NewLine);
                File.AppendAllText(path, timestamp + blueBalls + Environment.NewLine);
                break;
            //Player takes damage
            case 3:
                break;
            //Player deals damage
            case 4:
                break;
        }
    }
}