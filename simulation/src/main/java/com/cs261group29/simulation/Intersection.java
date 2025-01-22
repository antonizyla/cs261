package com.cs261group29.simulation;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Set;

public class Intersection {

    Set<Lane> northerlyLanes;
    Set<Lane> easterlyLanes;
    Set<Lane> southerlyLanes;
    Set<Lane> westerlyLanes;

    Queue<vehicle> northerlyVehicles = new LinkedList<>();
    Queue<vehicle> southerlyVehicles = new LinkedList<>();
    Queue<vehicle> westerlyVehicles = new LinkedList<>();
    Queue<vehicle> easterlyVehicles = new LinkedList<>();

    Parameters flowRates;

    int simulationClock; // take time in minutes

    Summary stats;
    
    public Intersection(){
        // create a basic 4 lane intersection
        // northerly lanes
        northerlyLanes.add(new Lane(Directions.NORTH, Arrays.asList(Directions.SOUTH, Directions.EAST))); // left lane going south
        northerlyLanes.add(new Lane(Directions.NORTH, Arrays.asList(Directions.SOUTH, Directions.WEST))); // right lane going south
        // westerly lanes
        westerlyLanes.add(new Lane(Directions.WEST, Arrays.asList(Directions.NORTH, Directions.EAST)));
        westerlyLanes.add(new Lane(Directions.WEST, Arrays.asList(Directions.EAST,Directions.SOUTH)));
        // southerly lanes
        northerlyLanes.add(new Lane(Directions.SOUTH, Arrays.asList(Directions.NORTH, Directions.WEST)));
        northerlyLanes.add(new Lane(Directions.SOUTH, Arrays.asList(Directions.NORTH, Directions.EAST)));
        // easterly lanes
        easterlyLanes.add(new Lane(Directions.EAST, Arrays.asList(Directions.WEST, Directions.SOUTH)));
        easterlyLanes.add(new Lane(Directions.EAST, Arrays.asList(Directions.WEST, Directions.NORTH)));
    
        flowRates = new Parameters();

        addHourlyVehciles();

        simulationClock = 0;

        // this is a basic 4 lane intersection
    }

    private void addHourlyVehciles(){
        // create vehicles coming from east
        for (int i = 0; i < flowRates.easterly.flowToWest; i++){
            easterlyVehicles.add(new vehicle(Directions.WEST, Directions.EAST));
        }
        for (int i = 0; i < flowRates.easterly.flowToNorth; i++){
            easterlyVehicles.add(new vehicle(Directions.NORTH, Directions.EAST));
        }
        for (int i = 0; i < flowRates.easterly.flowToSouth; i++){
            easterlyVehicles.add(new vehicle(Directions.SOUTH, Directions.EAST));
        }

        // create vehicles coming from west
        for (int i = 0; i < flowRates.westerly.flowToEast; i++){
            easterlyVehicles.add(new vehicle(Directions.EAST, Directions.WEST));
        }
        for (int i = 0; i < flowRates.westerly.flowToNorth; i++){
            easterlyVehicles.add(new vehicle(Directions.NORTH, Directions.WEST));
        }
        for (int i = 0; i < flowRates.westerly.flowToSouth; i++){
            easterlyVehicles.add(new vehicle(Directions.SOUTH, Directions.WEST));
        }

        // create vehicles coming from north
        for (int i = 0; i < flowRates.northerly.flowToWest; i++){
            easterlyVehicles.add(new vehicle(Directions.WEST, Directions.NORTH));
        }
        for (int i = 0; i < flowRates.northerly.flowToEast; i++){
            easterlyVehicles.add(new vehicle(Directions.EAST, Directions.NORTH));
        }
        for (int i = 0; i < flowRates.northerly.flowToSouth; i++){
            easterlyVehicles.add(new vehicle(Directions.SOUTH, Directions.NORTH));
        }

        // create vehicles coming from south
        for (int i = 0; i < flowRates.southerly.flowToWest; i++){
            easterlyVehicles.add(new vehicle(Directions.WEST, Directions.SOUTH));
        }
        for (int i = 0; i < flowRates.southerly.flowToNorth; i++){
            easterlyVehicles.add(new vehicle(Directions.NORTH, Directions.SOUTH));
        }
        for (int i = 0; i < flowRates.southerly.flowToEast; i++){
            easterlyVehicles.add(new vehicle(Directions.EAST, Directions.SOUTH));
        }
    }

    public void runSimulation(){
        // run for 10 hours as an example
        while (simulationClock < 600){
            // assume that each car takes 10s to cross the intersection and that right
            // now only a single car can be in the intersection at a time
            
            // east-west traffic 
            if (simulationClock % 2 == 0){
                // compute which cars from the queues can go

            }else{ // north-south traffic
                
            }
        }
    }

}
