#pragma once
#include "mainMenu.hpp"
#include <se_export.hpp>
#ifdef __XBOX__
#include <map>
#include <string>
#endif

#ifdef __XBOX__
void showXboxSystemMenu();
#endif

class SE_EXPORT PauseMenu : public Menu {
  private:
    enum class Action { None, Resume, Exit, GreenFlag, Stop };
    Action pendingAction = Action::None;
    void requestAction(Action action);
    void finishAction(Action action);
#ifdef __XBOX__
    std::map<std::string, std::string> gameControls;
    bool backReleased = false;
    std::unique_ptr<MenuText> pointerMoveHelp;
    std::unique_ptr<MenuText> pointerClickHelp;
#endif
  public:
#ifdef __XBOX__
    ButtonObject *systemButton = nullptr;
#endif
    ControlObject *pauseControl = nullptr;
    ButtonObject *backButton = nullptr;
    ButtonObject *exitProjectButton = nullptr;
    ButtonObject *flagButton = nullptr;
    ButtonObject *stopButton = nullptr;
    ButtonObject *turboButton = nullptr;

    bool shouldUnpause = false;

    PauseMenu();
    ~PauseMenu();

    void init() override;
    void render() override;
    void cleanup() override;
};
