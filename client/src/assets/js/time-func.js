function convertUnixToTime (unixTime) {
    return new Date(unixTime);
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
    const timestamp = time.getHours() + ":" + 
        time.getMinutes() + ":" + 
        time.getSeconds() + "." +
        Math.round(time.getMilliseconds() / 100)
    return timestamp;
}

function getFullTime (time) {
    const fullTime = getDay(time) + ", " + 
        getDate(time) + " " + 
        getMonth(time) + " " + 
        getYear(time) + ", " + 
        getTimestamp(time);
    return fullTime;
}

let time = {
    convertUnixToTime,
    getDay,
    getMonth,
    getYear,
    getTimestamp,
    getFullTime
}
export default time;

