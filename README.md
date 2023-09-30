dependencies:
discord.py,
yt-dlp,
ffmpeg,
mpv,

Discord Commands

$addsong <url>  - queues a youtube video
$addfile - reads attachment from discord message and queues the media file

$qtime - sends the total queued time

$nextsong - sends the time until user's next song in the queue

$showlist - sends a list of all users and their queued songs

$inserts <index> <url> - Places a song in queue in position without counting as a play for the user. Must have Karaok role to use


$insertf <index> - Places a song in queue in position without counting as a play for the user. Must have Karaok role to use


$remove <index> - deletes a song at index

additional features:

notifies user when their song is next

notifies user when their song is up

queue limit
