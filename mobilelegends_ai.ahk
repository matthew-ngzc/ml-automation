Loop {
    try {
        content := FileRead("command.txt")

        ; === 8-WAY MOVEMENT ===
        if (content = "move_up") {
            Send "{w down}"
            Sleep 400
            Send "{w up}"
        }
        else if (content = "move_down") {
            Send "{s down}"
            Sleep 400
            Send "{s up}"
        }
        else if (content = "move_left") {
            Send "{a down}"
            Sleep 400
            Send "{a up}"
        }
        else if (content = "move_right") {
            Send "{d down}"
            Sleep 400
            Send "{d up}"
        }
        else if (content = "move_up_left") {
            Send "{w down}{a down}"
            Sleep 400
            Send "{w up}{a up}"
        }
        else if (content = "move_up_right") {
            Send "{w down}{d down}"
            Sleep 400
            Send "{w up}{d up}"
        }
        else if (content = "move_down_left") {
            Send "{s down}{a down}"
            Sleep 400
            Send "{s up}{a up}"
        }
        else if (content = "move_down_right") {
            Send "{s down}{d down}"
            Sleep 400
            Send "{s up}{d up}"
        }

        ; === SKILL CASTING ===
	else if (content = "spam_skills"){
	    Send "1"
	    Send "2"
	}

        ;else if (content = "press_1") {
        ;    Send "1"
        ;}
        ;else if (content = "press_2") {
        ;    Send "2"
        ;}
	;else if (content = "press_3") {
        ;    Send "3"
        ;}

    } catch {
        ; Optional: log error or ignore
    }

    Sleep 10
}

Esc::ExitApp
