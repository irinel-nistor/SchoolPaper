
import datetime


from google.appengine.ext import db

class Result(db.Model):
   grade = db.IntegerProperty()
   passed = db.BooleanProperty()
   passingGrade = db.IntegerProperty()
   attendee = db.UserProperty()
   supervizor = db.UserProperty()

class Test(db.Model):
  question1 = db.StringProperty(multiline=True)
  answer1 = db.StringProperty()
  points1 = db.IntegerProperty()
  
  question2 = db.StringProperty(multiline=True)
  answer2 = db.StringProperty()
  points2 = db.IntegerProperty()

  question3 = db.StringProperty(multiline=True)
  answer3 = db.StringProperty()
  points3 = db.IntegerProperty()

  passingGrade = db.IntegerProperty()
  startTime = db.DateTimeProperty()
  endTime = db.DateTimeProperty()
  supervizor = db.UserProperty()
  
  def correct(self,answer1,answer2,answer3):
     totalPoints = 0
     if self.answer1 == answer1:
        totalPoints += self.points1
     if self.answer2 == answer2:
        totalPoints += self.points2
     if self.answer3 == answer3:
        totalPoints += self.points3

     result = Result()
     result.passed = totalPoints >= self.passingGrade
     result.grade = totalPoints
     result.passingGrade = self.passingGrade
     return result
      
  