# Runs an 8 track looper in Sonic Pi
# New loops are triggered by a toggle switch, and a Pimoroni Unicorn Phat provides feedback
# Requires controlBox.py or a similar OSC client running on a remote computer (i.e. Raspberry Pi)

use_osc "192.168.1.103", 9090
use_bpm 120

t=8 #set buffer duration
i=0 #set counter for loop names
x=0 #set counter for loop display

# clear cached buffers
sample_free_all

# each flip of a switch records a new 8 bar sample
define :new_loop do
  nxt = i+=1     # increase counter by 1 for unique buffer names
  name = nxt.to_s.to_sym    # convert the integer to a string, then to a symbol (:name)
  puts name
  with_fx :record, buffer: buffer[name, t] do
    live_audio :guitar do
    end
  end
end

loop1 = buffer(:"1", t)
loop2 = buffer(:"2", t)
loop3 = buffer(:"3", t)
loop4 = buffer(:"4", t)
loop5 = buffer(:"5", t)
loop6 = buffer(:"6", t)
loop7 = buffer(:"7", t)
loop8 = buffer(:"8", t)

# flash unicorn phat to mark the beat while recording
define :unicorn_feedback do
  t.times do
    osc "/beat", 0, 1, 1
    sleep 0.15
    osc "/beat", 0, 0, 0
    sleep 0.85
  end
end

# display running loop count on the unicorn phat's top row
define :loop_counter do
  x = x+=1
  osc "/count", (x-1), 0.24, 1, 1
end

# wait for the state of the switch to change, call loop function and update counter each time
in_thread do
  live_loop :looper do
    sync '/osc/switch2'
    new_loop
    loop_counter
    unicorn_feedback
    cue :start_playback
  end
end

# play all available samples
in_thread do
  live_loop :player, sync: :start_playback do
    sample loop1
    sample loop2
    sample loop3
    sample loop4
    sample loop5
    sample loop6
    sample loop7
    sample loop8
    sleep t
  end
end
