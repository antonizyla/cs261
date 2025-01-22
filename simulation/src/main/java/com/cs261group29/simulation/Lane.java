package com.cs261group29.simulation;

import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Set;

public class Lane {
   Directions dirFrom; 
   Set<Directions> directionsTo;

   Queue<vehicle> currentVehicles = new LinkedList<>();

   public Lane(Directions from, List<Directions> directionTo){
      dirFrom = from;
      for (Directions dir : directionTo){
         directionsTo.add(dir);
      }
   }

   public Set<Directions> getDirectionsTo(){
      return directionsTo;
   }

   public boolean doesItGoTo(Directions dir){
      return directionsTo.contains(dir);
   }

   public Directions getDirFrom(){
      return dirFrom;
   }

}
