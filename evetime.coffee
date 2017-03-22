# Description:
#   Script to convert EVE time (UTC) to local player time
#
# Commands:
#   !evetime - Prints the current EVE time in the requester's current timezone
#   !evetime <timezone> - Prints the current EVE time in the requested timezone
#   !evetime <time> - Prints the EVE time specified by <time> (24-hour hour/minute notation only) in the requester's current timezone
#   !evetime <time> <timezone> - Prints the EVE time specified by <time> in the requested timezone
#   !evetime <timezone> <time> - Prints the EVE time specified by <time> in the requested timezone
#
# Notes:
#   Also requires the slack_time_bot flask app
#
# Author:
#   bhechinger

module.exports = (robot) ->
  #time_re = "(\d{1,2}:\d{2,2}|\d{3,4})"
  #time_zone_re = "(\D+)"

  #re = new RegExp("!evetime #{time_re} #{time_zone_re}")

  call_api = (msg, time, timezone) ->
    url = "https://aba.4amlunch.net/time_bot/#{msg.message.user.name}/#{msg.message.user.room}"
    data = []

    data.push "time=#{encodeURIComponent(time)}" if time
    data.push "tz=#{encodeURIComponent(timezone)}" if timezone

    url = url + "?" + data.join('&') if data

    robot.http(url)
      .get() (err, res, body) ->
        if err
          msg.send "Encountered an error :( #{err}"

  robot.hear /^!evetime$/i, (msg) ->
    call_api(msg, null, null)

  #robot.hear re, (msg) ->
  robot.hear /^!evetime (\d{1,2}:\d{2,2}|\d{3,4}) (\D+)$/i, (msg) ->
    call_api(msg, msg.match[1].replace(/:/, ""), msg.match[2])

  robot.hear /^!evetime (\D+) (\d{1,2}:\d{2,2}|\d{3,4})$/i, (msg) ->
    call_api(msg, msg.match[2].replace(/:/, ""), msg.match[1])

  robot.hear /^!evetime (\d{1,2}:\d{2,2}|\d{3,4})$/i, (msg) ->
    call_api(msg, msg.match[1], null)

  robot.hear /^!evetime (\D+)$/i, (msg) ->
    call_api(msg, null, msg.match[1])
