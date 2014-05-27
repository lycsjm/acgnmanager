import datetime


def getSeason(date=datetime.date.today()):
    '''
    return 2-tuple of datetime.date as anime start date range.
    consider some anime will start some days before season of given days,
    return will not exectally as same as season.

    example:
    >>> getSeason(datetime.date(2014, 1, 13))
    (datetime.date(2014, 12, 01), datetime.date(2014, 03, 01))
    >>> getseason(datetime.date(2014, 06, 12))
    (datetime.date(2014, 06, 01), datetime.date(2014, 09, 01))
    '''
    years = [date.year] * 5
    years[0] -= 1
    months = [12, 3, 6, 9, 12]
    season = (date.month - 1) // 3
    startdate = datetime.date(years[season], months[season], 1)
    enddate = datetime.date(years[season + 1], months[season + 1], 1)

    return (startdate, enddate)
