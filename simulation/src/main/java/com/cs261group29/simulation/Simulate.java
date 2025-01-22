package com.cs261group29.simulation;

public class Simulate {
    Intersection layout;
    Parameters inputs;
    Summary outputs;    

    public void setParams(Parameters param){
        inputs = param;
    }

    public Summary getSummary(){
        return outputs;
    }

}
