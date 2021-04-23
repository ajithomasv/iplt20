### Constant Variable

SOURCE_DIR = '..//HTML//'
TARGET_DIR = '..//OutputFIles//'
FNAME = '13_Delhi Capitals v Mumbai Indians _ Match 13, IPL 2021 Match Centre _ IPLT20.com.html'
PROCESSED_FILES = 'processed_files.txt'

TEAMS = {
    'Chennai Super Kings': 'CSK',
    'Delhi Capitals': 'DC',
    'Kolkata Knight Riders': 'KKR',
    'Mumbai Indians' : 'MI',
    'Punjab Kings' : 'PK',
    'Rajasthan Royals' : 'RR',
    'Royal Challengers Bangalore' : 'RCB',
    'Sunrisers Hyderabad' : 'SRH'
}


### Import Packages


import os
import requests
from lxml import html


def getBattingScoreCard(scoreCard):
    d = {}
    battingPos = 1

    battingSC = scoreCard.find_class('batsmen')
    d['batsman'] = []
    tableBody = battingSC[0][1]
    for tableRow in tableBody:
        battingRec = {}
        if tableRow.attrib['class'] == 'extra':
            d2 = {}
            for s in tableRow[1].text.strip().strip('()').split(','):
                d2[s.strip().split(' ')[0]] = int(s.strip().split(' ')[1])
            d['extras'] = d2
            #d['extras'] = tableRow[1].text.strip()
            d['extras']['runs'] = int(tableRow[2].text)
        elif tableRow.attrib['class'] == 'total':
            d2 = {}
            for s in tableRow[1].text.strip().strip('()').split(';'):
                d2[s.strip().split(' ')[1]] = float(s.strip().split(' ')[0])
            d['total'] = d2
            #d['total_info'] = tableRow[1].text.strip()
            d['total']['runs'] = int(tableRow[2].text)
        else:
            battingRec['battingPos'] = battingPos
            battingPos += 1
            battingRec['playerId'] = int(tableRow.attrib['data-player-id'])
            battingRec['playerName'] = tableRow[1].text
            battingRec['dismissal'] = tableRow[2].text
            battingRec['runs'] = int(tableRow[3].text)
            battingRec['balls'] = int(tableRow[4].text)
            battingRec['strikeRate'] = float(tableRow[5].text)
            battingRec['fours'] = int(tableRow[6].text)
            battingRec['sixes'] = int(tableRow[7].text)
            d['batsman'].append(battingRec)

    # Getting data of players who didnt bat
    didNotBat = scoreCard.find_class('remainingBatsmen')
    if(len(didNotBat) > 0):
        for batsman in didNotBat[0][1]:
            battingRec = {}
            battingRec['battingPos'] = battingPos
            battingPos += 1
            battingRec['playerId'] = int(batsman[0].attrib['data-player-id'])
            battingRec['playerName'] = batsman[0].text.strip()
            battingRec['dismissal'] = 'DID NOT BAT'
            battingRec['runs'] = 0
            battingRec['balls'] = 0
            battingRec['strikeRate'] = 0
            battingRec['fours'] = 0
            battingRec['sixes'] = 0
            d['batsman'].append(battingRec)

    return d


def getBowlingScoreCard(scoreCard):
    d = []

    bowlingSC = scoreCard.find_class('bowlers')

    tableBody = bowlingSC[0][1]
    for tableRow in tableBody:
        bowlingRec = {}
        bowlingRec['playerId'] = int(tableRow.attrib['data-player-id'])
        bowlingRec['playerName'] = tableRow[1].text
        bowlingRec['overs'] = float(tableRow[2].text)
        bowlingRec['runs'] = int(tableRow[3].text)
        bowlingRec['wickets'] = int(tableRow[4].text)
        bowlingRec['economy'] = float(tableRow[5].text)
        bowlingRec['dots'] = int(tableRow[6].text)
        d.append(bowlingRec)

    return d



def getFallOfWickets(scoreCard):
    d = []
    fallOfWickets = scoreCard.find_class('fallOfWicket')
    for fow in fallOfWickets[0][1]:
       d.append(fow.text.strip().strip(','))
    return d



def getInningsSummary(scoreCard):
    """
        gets the inninngs summary of 1 innings
        param: scoreCard should be the data of 1 innings
    """
    d = {}
    team = scoreCard.find_class('teamHeader')
    d['battingTeamName'] = team[0][0].text.strip('Innings').strip()
    d['runRate'] = float(team[0][1].text.strip('()').split(':')[1].strip())
    d['battingScoreCard'] = getBattingScoreCard(scoreCard)
    d['bowlingScoreCard'] = getBowlingScoreCard(scoreCard)
    d['fallOfWickets'] = getFallOfWickets(scoreCard)
    return d



def getMatchSummary(filePath, fileName):
    d = {}
    f = open(os.path.join(filePath, fileName))
    tree = html.fromstring(f.read())
    f.close()

    matchInfo = tree.find_class('matchInfo')
    scoreCard = tree.find_class('teamScorecard')

    d['matchNum'] = int(fileName.split('_')[0])
    d['team1'] = ''
    d['team2'] = ''
    d['tossWonBy'] = matchInfo[0][0][0].text_content().split(':')[1].strip().split(',')[0]
    d['tossDecision'] = matchInfo[0][0][0].text_content().split(':')[1].strip().split(',')[1].split(' ')[-1]
    d['manOfTheMatch'] = matchInfo[0][0][1].text_content().split(':')[1].strip()
    d['venue'] = matchInfo[0][0][2].text_content().split(':')[1].strip()
    d['umpires'] = matchInfo[0][0][3].text_content().split(':')[1].strip().split(', ')
    d['referee'] = matchInfo[0][0][4].text_content().split(':')[1].strip()
    d['teamWon'] = ''
    d['firstInnings'] = getInningsSummary(scoreCard[0])
    d['secondInnings'] = getInningsSummary(scoreCard[1])
    d['team1'] = d['firstInnings']['battingTeamName']
    d['team2'] = d['secondInnings']['battingTeamName']
    d['teamWon'] = d['firstInnings']['battingTeamName'] if d['firstInnings']['battingScoreCard']['total']['runs'] > d['secondInnings']['battingScoreCard']['total']['runs'] else d['secondInnings']['battingTeamName']

    return d



def getFilesList(sourceFilePath):
    """
        Get the list of files which are not yet processed
        reference: processed_files.txt
    """
    flist = []
    files = os.listdir(sourceFilePath)

    f = open(os.path.join(sourceFilePath,PROCESSED_FILES))
    processedFiles = list(map(lambda x: x.strip(), f.readlines()))
    f.close()
    files.sort()

    for file in files:
        if file.endswith('.html') and file not in processedFiles:
            flist.append(file)
    return flist


def processFiles(sourceFilePath, targetFilePath):

    sourceFiles = getFilesList(sourceFilePath)
    processedFiles = open(os.path.join(sourceFilePath,PROCESSED_FILES), 'a')

    for file in sourceFiles:
        outFileName = 'IPL_2021_Match_' + file.split('_')[0]
        outFileName += '_' + TEAMS[file.split('_')[1].strip().split('v')[0].strip()]
        outFileName += '_' + TEAMS[file.split('_')[1].strip().split('v')[1].strip()]
        outFileName += '.txt'
        outputFile = open(os.path.join(targetFilePath, outFileName), 'a')

        d = getMatchSummary(sourceFilePath, file)
        outputFile.write(d)
        outputFile.write('\n')
        outputFile.close()

        processedFiles.write(file + '\n')

    processedFiles.close()

if __name__ == '__main__':
    
    processFiles(SOURCE_DIR, TARGET_DIR)
