; === Key Bindings ===
key_bindings := Map(
    "skill_1", ["k"],
    "skill_2", ["l"],
    "skill_3", [";"],
    "skill_4", ["'"],
    "upgrade_skill_1", ["l"],
    "upgrade_skill_2", ["o"],
    "upgrade_skill_3", ["p"],
    "upgrade_skill_4", ["["],
    "skill_1_extra", ["i"],
    "skill_2_extra", ["o"],
    "skill_3_extra", ["p"],
    "skill_4_extra", ["["],
    "move_up", ["w"],
    "move_down", ["s"],
    "move_left", ["a"],
    "move_right", ["d"],
    "move_up_right", ["w", "d"],
    "move_up_left", ["w", "a"],
    "move_down_right", ["s", "d"],
    "move_down_left", ["s", "a"],
    "attack_basic", ["j"],
    "attack_minion", ["n"],
    "attack_turret", ["u"],
    "spell", ["h"],
    "regen", ["g"],
    "recall", ["b"],
    "buy", ["Space"],
    "chat", ["Enter"],
    "skill_item", ["f"]
)


; === Movement State Tracker ===
prev_keys := []  ; Stores previously held keys across frames
combined_keys := []


; === Function: Hold Keys ===
; This function simulates holding down multiple keys simultaneously.
HoldKeys(keys) {
    global prev_keys
    ; Debugging
    ; try
    ;     FileObj := FileOpen("log.txt", "a")
    ; catch as Err
    ; {
    ;     return
    ; }
    ; for _, k in keys{
    ;     FileObj.WriteLine(k)
    ; }
    ; FileObj.WriteLine("===")


    ; Release keys no longer in the current keylist
    for _, k in prev_keys {
        found := false
        ;search for the key in the current keylist
        for _, key in keys {
            if (key = k) {
                found := true
                break
            }
        }
        ; if the key is not found in the current keylist, release it
        if (!found) {
            SendInput "{" k " up}"
        }
    }

    ; Press new keys not already held
    for _, k in keys {
        found := false
        ;search for the key in the previous keylist
        for _, key in prev_keys {
            if (key = k) {
                found := true
                break
            }
        }
        ;cannot find means it's a new key
        if (!found) {
            SendInput "{" k " down}"
        }
    }
    prev_keys := keys.Clone()  ; Store for next frame
}



; === Function: Execute semantic command ===
ExecuteCommand(cmd) {
    global key_bindings, combined_keys


    if (cmd = "spam_skills") {
        combined_keys.Push(key_bindings["skill_1"]*)
        combined_keys.Push(key_bindings["skill_2"]*)
        return
    }

    if (key_bindings.Has(cmd)!==0) {
        combined_keys.Push(key_bindings[cmd]*)
        return
    }

    ; SysGet, MonitorWorkAreaRight, 78
    ; SysGet, MonitorWorkAreaBottom, 79
    ; Tooltip, Unknown command: %cmd%, % MonitorWorkAreaRight - 200, % MonitorWorkAreaBottom - 100
    ; Sleep 300
    ; Tooltip
}



; === Main Command Reader Loop ===
Loop {
    ;read from command.txt and put into variable "raw"
    content := FileRead("command.txt")
    if (content != "") {
        ;delete command.txt
        ;FileDelete("command.txt")
        combined_keys := []
        ; Split the content into lines
        Loop Parse, content, "`n", "`r"
        {
            cmd := A_LoopField ;extract the line
            if (cmd = "")
                continue
            ;put all the commands into the array "combined_keys"
            ExecuteCommand(cmd)
        }

        ; Execute the commands in the array "combined_keys" simultaneously
        if (combined_keys.Length > 0) {
            HoldKeys(combined_keys)
        }
    }
    Sleep 20 ;needed so that the CPU doesn't go crazy
}

;Exit on Esc key
Esc::ExitApp
