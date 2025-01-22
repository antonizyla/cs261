package com.cs261group29.simulation;

class flow {
    public int inflow;
    public int flowToNorth;
    public int flowToEast;
    public int flowToSouth;
    public int flowToWest;

    public flow(int in, int n, int e, int s, int w){
        inflow=in;
        flowToNorth = n;
        flowToEast = e;
        flowToSouth = s;
        flowToWest = w;
    }
}

public class Parameters {
    public flow northerly;
    public flow easterly;
    public flow southerly;
    public flow westerly;    

    // this would have all the other stuff
    int numLanes = 4; // assume each way on all roads

    public Parameters(){
        northerly = new flow(300, 200, 50, 0, 50);
        southerly = new flow(250, 0, 50, 150, 50);
        easterly = new flow(150, 50, 50, 50, 0);
        westerly = new flow(100, 25, 0, 25, 50);
    }
}
