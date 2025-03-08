class ResultSet:
    def __init__(self, northRoad, eastRoad, southRoad, westRoad, overallScore):
        self.northRoad = northRoad
        self.eastRoad = eastRoad
        self.southRoad = southRoad
        self.westRoad = westRoad
        self.overallScore = overallScore

    def getNorthRoad(self):
        return self.northRoad

    def getEastRoad(self):
        return self.eastRoad

    def getSouthRoad(self):
        return self.southRoad

    def getWestRoad(self):
        return self.westRoad

    def getScore(self):
        return self.overallScore
