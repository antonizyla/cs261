package com.cs261group29.simulation;

public class vehicle {
   int vehicleid;

   Directions directionTo;
   Directions directionFrom;

   public vehicle(Directions dirTo, Directions dirFrom){
    directionFrom = dirFrom;
    directionTo = dirTo;
   }
}
