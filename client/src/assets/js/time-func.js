function convertUnixToTime (unixTime) {
    const t = unixTime;
    return new Date(t);
}

function getDay (time) {
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"];
    return dayNames[time.getDay()];
}

function getDate (time) {
    return time.getDate();
}

function getMonth (time) {
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
    return monthNames[time.getMonth()];
}

function getYear (time) {
    return time.getFullYear();
}

function getTimestamp (time) {
    var timestamp = time.getHours() + ":" + 
        time.getMinutes() + ":" + 
        time.getSeconds() + ".";
    var miliseconds = Math.round(time.getMilliseconds() / 100);
    if (miliseconds == 10) { miliseconds = 0; }
    timestamp = timestamp + miliseconds
    return timestamp
}

function getTimestampFromUnix (unixTime) {
    return getTimestamp(convertUnixToTime(unixTime));
}

function getFullTime (time) {
    const fullTime = getDay(time) + ", " + 
        getDate(time) + " " + 
        getMonth(time) + " " + 
        getYear(time) + ", " + 
        getTimestamp(time);
    return fullTime;
}

function getFullTimeFromUnix (unixTime) {
    return getFullTime(convertUnixToTime (unixTime));
}

let time = {
    convertUnixToTime,
    getDay,
    getMonth,
    getYear,
    getTimestamp,
    getFullTime,
    getTimestampFromUnix,
    getFullTimeFromUnix
}
export default time;

