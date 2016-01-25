highestCount = 0
commonYr = 0
countList = []
years = [1994, 1993, 1994, 1994, 2009, 2009, 2010, 2009]
#years = [1994, 1994, 1998, 2009]
distinctYears = list(set(years))
distinctYears = sorted(distinctYears, key=int, reverse=True)
print(distinctYears)
#remove years that are close together from distinct list
index = 0
for distYear in distinctYears:
    for distYearOth in distinctYears:
        if(distYear != distYearOth):
            if(abs(int(distYear) - int(distYearOth)) <= 3):
                print("Deleting: " + str(distinctYears[index]))
                del distinctYears[index]
    index += 1

print(distinctYears)

for distYear in distinctYears:
    count = 0
    print("loop " + str(count))
    for year in years:
        print("Comparison: " + str(distYear) + " " + str(year))
        if(abs(int(year) - int(distYear)) <= 3):
            count += 1
    print(str(count))
    if(count > highestCount):
        highestCount = count
        commonYr = distYear
    countList.append(count)
countList = sorted(countList, key=int, reverse=True)
print(countList)

print(commonYr)
print(highestCount)
