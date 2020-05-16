from datetime import date

def extract_date(date_string):
    date_tuple = tuple(map(int, date_string.split("-")))
    return(date(date_tuple[0], date_tuple[1], date_tuple[2]))

def format_date(date_obj):
    return(date_obj.strftime("%Y-%m-%d"))

def is_growing(close):
	for i in range(0,len(close)-1):
		if close[i]>close[i+1]:
			return False
	return True

def is_falling(close):
	for i in range(0,len(close)-1):
		if close[i]<close[i+1]:
			return False
	return True
