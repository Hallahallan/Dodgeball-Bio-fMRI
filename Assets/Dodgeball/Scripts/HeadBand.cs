using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeadBand : MonoBehaviour
{
    public HeadBand headBand;
    public Material greenBand;
    public Material yellowBand;
    public Material redBand;
    // Start is called before the first frame update
    public void Start()
    {
        //Start with a green band
        // headBand.GetComponent<Renderer> ().material = greenBand;
    }
    public void setGreenBand()
    {
        //Set green band on restart
        headBand.GetComponent<Renderer> ().material = greenBand;
    }
    public void setYellowBand()
    {
        //Set yellow band on hit
        headBand.GetComponent<Renderer> ().material = yellowBand;
    }
    public void setRedBand()
    {
        //Set red band on hit
        headBand.GetComponent<Renderer> ().material = redBand;
    }
    // Update is called once per frame
    void Update()
    {
        // headBand.GetComponent<Renderer> ().material = greenBand;
    }
}
