from rules.Rule import Rule
import nltk
import nltk.data
import re
import difflib

class ContextRule(Rule):
    upperLimit = 150
    lowerLimit = 150
    samenessThreshold = .70

    def __init__(self, name):
        self.name = name

    #symtomList is a list of lists
    def run(self, record, symptomList):
        matched = False
        #matches diagnosis, diagnosed, diagnos or multiple sclerosis or ms and returns the upperlimit amount of characters after and the lowerlimit of characters before
        regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}'

        #regex = r'.{0,' + str(self.lowerLimit) + '}diagnos.{0,' + str(self.upperLimit) + '}|.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' + str(self.lowerLimit) + '}ms.{0,' + str(self.upperLimit) + '}'
        #regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' + str(self.lowerLimit) + '}ms.{0,' + str(self.upperLimit) + '}'
        matches = re.findall(regex, record, re.IGNORECASE)

        for match in matches:
            #check for negating language here
            regex = r'\sno.\s|can\'t|cannot|negative'
            #regex = r'\sno.\s|can\'t|cannot|negative|hardly|unknown|scarcely|shouldn\'t|should\snot|won\'t|will\snot|don\'t|do\snot|never|neither|nor|isn\'t|is\snot|wouldn\'t|would\snot'
            negMatches = re.findall(regex, match)
            if(len(negMatches) == 0):
                '''
                #use NLP to pick out the noun and see if it's a symptom or MS
                tokens = nltk.word_tokenize(match)
                tagged = nltk.pos_tag(tokens)
                for tag in tagged:
                    if(matched == True):
                        break
                    #find out if it's a noun
                    if(tag[1] == 'NN'):
                        #find out if the noun is in the symptom list
                        for symptoms in symptomList:
                            if(matched == True):
                                break
                            for symptom in symptoms:
                                samenessRatio = difflib.SequenceMatcher(None, tag[0], symptom).ratio()
                                if(samenessRatio >= self.samenessThreshold):
                                    matched = True
                                    break
                '''


                regex = r'.{0,' + str(self.lowerLimit) + '}multiple\ssclerosis.{0,' + str(self.upperLimit) + '}|.{0,' + str(self.lowerLimit) + '}\sms\s.{0,' + str(self.upperLimit) + '}'
                matches = re.findall(regex, match, re.IGNORECASE)
                for match in matches:
                    regex = r'\sno.\s|can\'t|cannot|negative'
                    #regex = r'\sno.\s|can\'t|cannot|negative|hardly|unknown|scarcely|shouldn\'t|should\snot|won\'t|will\snot|don\'t|do\snot|never|neither|nor|isn\'t|is\snot|wouldn\'t|would\snot'
                    negMatches = re.findall(regex, match)
                    if(len(negMatches) == 0):
                        matched = True
                        break

        return matched
