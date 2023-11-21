import pandas as pd

def personal_detection(df):
   # df = pd.read_csv("Cautious/cautious02.csv")
   # df = pd.read_csv("Calmly/calmly03.csv")
   # df = pd.read_csv("Aggressive/aggressive02.csv")

   last_distance = df.iloc[-1]
   final_distance = last_distance["Distance"]

   if final_distance != 100:
      return "You cant finish the line", 0

   # Calculate Speed out the roundabout
   average_speed_out = sum_speed(df)
   average_speed_out1 = average_speed_out[0] / average_speed_out[1]

   # Calculate Speed all
   average_speed_all = sum(df["Speed"]) / len(df["Speed"])

   # Calculate Speed before enter crosswalk
   average_speed_cross = sum_speed_cross(df)
   average_speed_cross1 = average_speed_cross[0] / average_speed_cross[1]

   #Calculate a final time
   last_row = df.iloc[-1]
   final_time = last_row["Time"]

   # print("Final Time:", final_time)

   # print("Average Speed All:",average_speed_all)

   # print("Average Speed Out:",average_speed_out1)

   # print("Average Speed Cross:",average_speed_cross1)

   result = result_and(final_time, average_speed_out1, average_speed_cross1)
   # result = result_and(156, 32, 29)
   # print("result", result)
   personality,data = personality_detection(result)

   return personality,data
# ---------------------------------------------------------------- Start Results --------------------------------

def personality_detection(data):
   if data <= 0.4:
      result = "Aggressive"
   elif data >= 0.6:
      result = "Calmly"
   else:
      result = "Cautious"

   return result,data

# ---------------------------------------------------------------- Get a Slope ----------------------------------------------------------------

def getSlope(x1, y1, x2, y2):
    #Avoid zero division error of vertical line for shouldered trapmf
    try:
        slope = (y2 - y1) / (x2 - x1)
    except ZeroDivisionError:
        slope = 0
    return slope

def getYIntercept(x1, y1, x2, y2):
    m = getSlope(x1, y1, x2, y2)
    if y1 < y2:
        y = y2
        x = x2
    else:
        y = y1
        x = x1
    return y - m * x

def result_and(final_time, average_speed_out1, average_speed_cross1):
   sum_ = []
   data1 = [time_low(final_time), speed_round_slow(average_speed_out1), speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data1))
   # print("Data1", data1)
   data2 = [time_low(final_time) , speed_round_slow(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data2))
   # print("Data2", data2)
   data3 = [time_low(final_time) , speed_round_slow(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data3))
   # print("Data3", data3)
   data4 = [time_low(final_time) , speed_round_mid(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data4))
   # print("Data4", data4)
   data5 = [time_low(final_time) , speed_round_mid(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data5))
   # print("Data5", data5)
   data6 = [time_low(final_time) , speed_round_mid(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data6))
   # print("Data6", data6)
   data7 = [time_low(final_time) , speed_round_fast(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data7))
   # print("Data7", data7)
   data8 = [time_low(final_time) , speed_round_fast(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data8))
   #print("Data8", min(data8))
   data9 = [time_low(final_time) , speed_round_fast(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data9))
   #print("Data9", data9)

   data10 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data10))
   #print("Data10", data10)
   data11 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   #print(time_mid(final_time), speed_round_slow(average_speed_out1), speed_cross_mid(average_speed_cross1))
   sum_.append(min(data11))
   #print("Data11", data11)
   data12 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data12))
   #print("Data12", data12)
   data13 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data13))
   #print("Data13", data13)
   data14 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data14))
   #print("Data14", data14)
   data15 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data15))
   #print("Data15", data15)
   data16 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data16))
   #print("Data16", data16)
   data17 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data17))
   #print("Data17", data17)
   data18 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data18))
   #print("Data18", data18)

   data19 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data19))
   #print("Data19", data19)
   data20 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data20))
   #print("Data20", data20)
   data21 = [time_mid(final_time) , speed_round_slow(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data21))
   #print("Data21", data21)
   data22 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data22))
   #print("Data22", data22)
   data23 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data23))
   #print("Data23", data23)
   data24 = [time_mid(final_time) , speed_round_mid(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data24))
   #print("Data24", data24)
   data25 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_slow(average_speed_cross1)]
   sum_.append(min(data25))
   #print("Data25", data25)
   data26 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_mid(average_speed_cross1)]
   sum_.append(min(data26))
   #print("Data26", data26)
   data27 = [time_mid(final_time) , speed_round_fast(average_speed_out1) , speed_cross_fast(average_speed_cross1)]
   sum_.append(min(data27))
   
   # 9 rule based for testing
   out1 = test_cautious(sum_[0])
   out2 = test_cautious(sum_[1])   
   out3 = test_aggressive(sum_[2])

   out4 = test_cautious(sum_[3])   
   out5 = test_cautious(sum_[4])   
   out6 = test_aggressive(sum_[5])

   out7 = test_aggressive(sum_[6])
   out8 = test_aggressive(sum_[7])
   out9 = test_aggressive(sum_[8])

   out10 = test_calmly(sum_[9])
   out11 = test_calmly(sum_[10])
   out12 = test_aggressive(sum_[11])

   out13 = test_calmly(sum_[12])
   out14 = test_cautious(sum_[13])
   out15 = test_aggressive(sum_[14])

   out16 = test_cautious(sum_[15])
   out17 = test_cautious(sum_[16])
   out18 = test_aggressive(sum_[17])

   out19 = test_calmly(sum_[18])
   out20 = test_calmly(sum_[19])
   out21 = test_aggressive(sum_[20])

   out22 = test_calmly(sum_[21])
   out23 = test_cautious(sum_[22])
   out24 = test_aggressive(sum_[23])

   out25 = test_aggressive(sum_[24])
   out26 = test_aggressive(sum_[25])
   out27 = test_aggressive(sum_[26])


   find_max = []
   for i in range(100):
      # test = max(out1[i], out2[i], out3[i], out4[i], out5[i], out6[i], out7[i], out8[i], out9[i])
      # print(test)
      find_max.append(max(out1[i], out2[i], out3[i], out4[i], out5[i], out6[i], out7[i], out8[i], out9[i], out10[i], out11[i], out12[i], out13[i], out14[i], out15[i], out16[i], out17[i], out18[i], out19[i], out20[i], out21[i], out22[i], out23[i], out24[i], out25[i], out26[i], out27[i]))
      #print("Max:", find_max)

   # out = []
   # for i in range(27):
   #    out[i] = test_aggressive[sum_[i]]
   
   # ยังทำไม่เสร็จ
   # find_max = []
   # for i in range(27):
   #    for j in range(100):
   #       find_max.append(max(out[i][j], out[i][i], out3[i], out4[i], out5[i], out6[i], out7[i], out8[i], out9[i], out10[i], out11[i], out12[i], out13[i], out14[i], out15[i], out16[i], out17[i], out18[i], out19[i], out20[i], out21[i], out22[i], out23[i], out24[i], out25[i], out26[i], out27[i]))
   

   # find cog 
   sum_xi_i = []
   sum_xi = []
   
   for i in range(len(find_max)):
      sum_xi_i.append(find_max[i]*i)
      sum_xi.append(find_max[i])
   
   cog = sum(sum_xi_i)/(sum(sum_xi)*100)
   print("Cog = ", cog)
   return cog
   #result = max(sum_)
   # result = data1 or data2 or data3 or data4 or data5 or data6 or data7 or data8 or data9 or data10 or data11 or data12 or data13 or data14 or data15 or data16 or data17 or data18 or data19 or data20 or data21 or data22 or data23 or data24 or data25 or data26 or data27

# ---------------------------------------------------------------- Graph functions ----------------------------------------------------------------

def test_aggressive(in_mf):
   # aggressive_list = []
   aggressive_list = list(range(0,100))
   point = [0,1,40,0]
    
   for i in range(len(aggressive_list)):
      if i < 40:
         aggressive_list[i] = -0.025 * (i+1) + 1
      else:
         aggressive_list[i] = 0
      
   for j in range(40):
      if in_mf < aggressive_list[j]:
         aggressive_list[j] = in_mf
   
   return aggressive_list

def test_cautious(in_mf):
   cautious_list = list(range(0,100))
   point = [0, 10,50,90]
   
   for i in range(len(cautious_list)):
      if i <=10 :
         cautious_list[i] = 0
      elif 10 < i < 50 :
         cautious_list[i] = (0.025 * i) - 0.25
      elif 50 <= i < 90 :
         cautious_list[i] = (-0.025 * i) + 2.25
      elif 90 <= i <= 100 :
         cautious_list[i] = 0
      
      
   for j in range(10,90):
      if in_mf < cautious_list[j]:
         cautious_list[j] = in_mf
   
   return cautious_list

def test_calmly(in_mf):
   calmly_list = list(range(0,100))
   point = [60,100,1000,1000]
    
   for i in range(len(calmly_list)):
        if i >= 60:
            calmly_list[i] = 0.025 * i - 1.5
        else:
            calmly_list[i] = 0
      #   print(i," = ", calmly_list[i])

      
   for j in range(60,100):
      if in_mf < calmly_list[j]:
         calmly_list[j] = in_mf
   
   return calmly_list

#---------------------------------------------------------------- Start Time Detection --------------------------------

def time_low(data):
   points = [-186, 1, 180, 250]
   if (data <= 120):
      result = 1
   elif (data > 300):
      result = 0
   else: 
      result = trapmf(data, points)
   return result

def time_mid(data):
   points = [190, 230, 380]
   if (data == 300):
      result = 1
   else:
      result = trimf(data, points);
   return result
      
def time_high(data):
   points = [250, 300, 10000]
   if (data >= 500):
      result = 1
   else:
      result = trimf(data, points);
   return result

# ---------------------------------------------------------------- Start Speed_roundabout ----------------------------------------------------------------
def speed_round_slow(data):
   points = [-1000, 9, 15]
   if (data <= 0):
      result = 1
   else:
      result = trimf(data, points);
   return result

def speed_round_mid(data):
   points = [8, 15, 30]
   # if (data == 25):
   #    result = 1
   # else:
   result = trimf(data, points);
   return result

def speed_round_fast(data):
   points = [15, 1000, 1000]
   # if (data >= 50):
   #    result = 1
   # else:
   result = trimf(data, points);
   return result

# ---------------------------------------------------------------- Start Speed Crosswalk----------------------------------------------------------------

def speed_cross_slow(data):
   points = [-1000, 0, 10, 20]
   if data < 10:
      result = 1
   elif data >25:
      result = 0
   else:
      result = trapmf(data, points)
   return result      

def speed_cross_mid(data):
   points = [9, 20, 30]
   result = trimf(data, points)
   return result

def speed_cross_fast(data):
   points = [20, 42, 1000, 1000]
   result = trapmf(data, points)
   return result

# ---------------------------------------------------------------- Classify Data --------------------------------

def sum_speed(df):
   sum_speed = 0
   count = 0

   for i in range(0, len(df["Speed"])):
      passed_roundabout = df["Circus entry"]
      speed = df["Speed"]
      if (passed_roundabout[i] == 1) or (passed_roundabout[i] == 2) or (passed_roundabout[i] == 3) or (passed_roundabout[i] == 4) or (passed_roundabout[i] == 5) or (passed_roundabout[i] == 6 ) or (passed_roundabout[i] == 7) or (passed_roundabout[i] == 8) or (passed_roundabout[i] == 9) or (passed_roundabout[i] == 10):
         sum_speed += speed[i]
         count += 1
   
   return sum_speed, count

def sum_speed_in(df):
   sum_speed = 0
   count = 0

   for i in range(0, len(df["Speed"])):
      passed_roundabout = df["Circus entry"]
      speed = df["Speed"]
      if (passed_roundabout[i] == 1) or (passed_roundabout[i] == 2) or (passed_roundabout[i] == 3) or (passed_roundabout[i] == 4) or (passed_roundabout[i] == 5) or (passed_roundabout[i] == 6 ) or (passed_roundabout[i] == 7) or (passed_roundabout[i] == 8) or (passed_roundabout[i] == 9) or (passed_roundabout[i] == 10):
         sum_speed += speed[i]
         count += 1
   
   return sum_speed, count


def sum_speed_cross(df):
   sum_speed = 0
   count = 0

   for i in range(0, len(df["Speed"])):
      passed_cross = df["Crosswalk entry"]
      speed = df["Speed"]
      if (passed_cross[i] == 1) or (passed_cross[i] == 2) or (passed_cross[i] == 3) or (passed_cross[i] == 4) or (passed_cross[i] == 5) or (passed_cross[i] == 6):
         sum_speed += speed[i]
         count += 1
   
   return sum_speed, count

# ---------------------------------------------------------------- Tramf ----------------------------------------------------------------

def trapmf(x, points):
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    pointD = points[3]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeCD = getSlope(pointC, 1, pointD, 0)
    yInterceptAB = getYIntercept(pointA, 0, pointB, 1)
    yInterceptCD = getYIntercept(pointC, 1, pointD, 0)
    result = 0
    if x > pointA and x < pointB:
        result = slopeAB * x + yInterceptAB
    elif x >= pointB and x <= pointC:
        result = 1
    elif x > pointC and x < pointD:
        result = slopeCD * x + yInterceptCD
    return result

# ---------------------------------------------------------------- Trimf ----------------------------------------------------------------

def trimf(x, points): 
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeBC = getSlope(pointB, 1, pointC, 0)
    result = 0
    if x >= pointA and x <= pointB:
        result = slopeAB * x + getYIntercept(pointA, 0, pointB, 1)
    elif x >= pointB and x <= pointC:
        result = slopeBC * x + getYIntercept(pointB, 1, pointC, 0)
    return result

if __name__ == "__main__":
   main()