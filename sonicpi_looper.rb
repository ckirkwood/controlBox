# 8 track audio looper for Sonic Pi
# Controlled via OSC commands (i.e. controlBox.py)

use_osc "192.168.1.103", 9090
use_bpm 120
set_volume! 2

t=8 #set buffer duration
i=0 #set counter for loop names
x=-1 #set counter for loop display
xx=-2 #set counter for beat display

# clear LEDs
osc "/clear_all"
sample_free_all

# heartbeat
in_thread do
  live_loop :heartbeats do
    cue :tick
    sleep 1
  end
end

# kick drum as metronome
in_thread do
  live_loop :bd do
    sync :tick
    sample :drum_heavy_kick
  end
end

# called on each flip of switch 1; records a new 8 bar sample with a unique buffer name
define :new_loop do
  nxt = i+=1     # increase counter by 1 for a unique buffer name
  name = nxt.to_s.to_sym    # convert the integer to a string, then to a symbol (:name)
  if nxt > 8     # when 8 loops are full, go back to 1 and overwrite as each buffer is filled again
    i=0
  end
  with_fx :record, buffer: buffer[name, t] do
    live_audio :guitar do
    end
  end
end

# chose the lead-in time before recording starts, flash unicorn phat on the beat
define :count_in do |beats|
  beats.times do
    sync :tick
    b = xx+=2
    osc "/beat", b, 0.25, 1, 1
    sleep 0.15
    osc "/beat", b, 0, 0, 0
    sleep 0.85
    if b > 4
      xx = -2
      osc "/hsv", 0, 0, 0
    end
  end
end

# flash unicorn phat on the beat while recording
# the corresponding function in controlBox.py takes b as y-coordinates to flash 6x2 LED sections
define :unicorn_feedback do
  t.times do
    sync :tick
    b = xx+=2
    osc "/beat", b, 0, 1, 1
    sleep 0.15
    osc "/beat", b, 0, 0, 0
    sleep 0.85
    if b > 4
      xx = -2
      osc "/hsv", 0, 0, 0
    end
  end
end

# display running loop count on the unicorn phat's top row
define :loop_counter do
  c = x+=1
  if c >= 8     # reset after 8 loops
    osc "/clear_counter"
    x = 0
    osc "/count", 0, 0.7, 1, 1
  end
  osc "/count", c, 0.7, 1, 1
end

# wait for the state of the switch to change, call loop functions and update counter each time
in_thread do
  live_loop :looper, sync: :tick do
    sync '/osc/switch1'
    count_in 4
    loop_counter
    new_loop
    unicorn_feedback
    cue :start_playback     # replay buffers at the end of each new loop
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



# play all available samples
in_thread do
  live_loop :player, sync: :start_playback do
    $one = sample loop1
    $two = sample loop2
    $three = sample loop3
    $four = sample loop4
    $five = sample loop5
    $six = sample loop6
    $seven = sample loop7
    $eight = sample loop8
    sleep t
  end
end

#in_thread do
#  live_loop :pots do
#    pot1, pot2, pot3, pot4, pot5, pot6, pot7, pot8 = sync '/osc/pots'
#    control $one, amp: pot1 / 127.0
#    control $two, amp: pot2 / 127.0
#    control $three, amp: pot3 / 127.0
#    control $four, amp: pot4 / 127.0
#    control $five, amp: pot5 / 127.0
#    control $six, amp: pot6 / 127.0
#    control $seven, amp: pot7 / 127.0
#    control $eight, amp: pot8 / 127.0
#    sleep t
#  end
#end
