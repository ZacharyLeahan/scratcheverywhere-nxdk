#include "pauseMenu.hpp"
#include "translation.hpp"
#include <renderer.hpp>
#include <runtime.hpp>
#include <speech_manager.hpp>
#include <utility>
#include <xbox_menu_trace.hpp>
#include <algorithm>
#ifdef __XBOX__
#include <filesystem.hpp>
#include <xbox_pointer_help.hpp>
#endif
#ifdef SE_XBOX_TRACE_GAME_STATE
#include <blockExecutor.hpp>
#include <log.hpp>
#endif

PauseMenu::PauseMenu() {
    init();
}

PauseMenu::~PauseMenu() {
    cleanup();
}

static std::string getTurboString() {
    return TranslationManager::getTranslation("ui.pause.turbo") + ": " + TranslationManager::getTranslation(Scratch::turbo ? "ui.settings.on" : "ui.settings.off");
}

void PauseMenu::init() {
#ifdef __XBOX__
    Scratch::freeUnusedCostumeImages();
#endif
#ifdef SE_XBOX_TRACE_GAME_STATE
    if (Scratch::stageSprite) {
        Log::log("Pause state snapshot:");
        for (const auto &[id, variable] : Scratch::stageSprite->variables) {
            Log::log(variable.name + "=" + BlockExecutor::getVariableValue(id, Scratch::stageSprite).asString());
        }
        Log::log("Runtime clones=" + std::to_string(Scratch::cloneCount) +
                 " threads=" + std::to_string(BlockExecutor::threads.size()));
        for (const auto &[id, list] : Scratch::stageSprite->lists) {
            Log::log("List " + list.name + " size=" + std::to_string(list.items.size()));
        }
        std::unordered_map<std::string, unsigned> cloneCounts;
        for (const auto *sprite : Scratch::sprites) {
            if (sprite->isClone) ++cloneCounts[sprite->name];
        }
        for (const auto &[name, count] : cloneCounts) {
            Log::log("Clone population " + name + "=" + std::to_string(count));
        }
    }
#endif
#ifdef __XBOX__
    gameControls = Input::inputControls;
    Input::applyControls();
#endif
    constexpr int buttons = 4;
    constexpr int space = (180 - 60) / buttons;

    pauseControl = new ControlObject();
    backButton = new ButtonObject("", "gfx/menu/buttonBack.svg", 375, 20, "gfx/menu/Ubuntu-Bold");

    exitProjectButton = new ButtonObject(TranslationManager::getTranslation("ui.pause.exit"), "gfx/menu/projectBox.svg", 200, 60, "gfx/menu/Ubuntu-Bold", true);
    exitProjectButton->text->setColor(Math::color(0, 0, 0, 255));

    flagButton = new ButtonObject(TranslationManager::getTranslation("ui.pause.flag"), "gfx/menu/projectBox.svg", 200, 60 + space, "gfx/menu/Ubuntu-Bold", true);
    flagButton->text->setColor(Math::color(0, 0, 0, 255));

    stopButton = new ButtonObject(TranslationManager::getTranslation("ui.pause.stop"), "gfx/menu/projectBox.svg", 200, 60 + space * 2, "gfx/menu/Ubuntu-Bold", true);
    stopButton->text->setColor(Math::color(0, 0, 0, 255));

    turboButton = new ButtonObject(getTurboString(), "gfx/menu/projectBox.svg", 200, 60 + space * 3, "gfx/menu/Ubuntu-Bold", true);
    turboButton->text->setColor(Math::color(0, 0, 0, 255));

    backButton->needsToBeSelected = false;

    pauseControl->buttonObjects.push_back(exitProjectButton);
    pauseControl->buttonObjects.push_back(flagButton);
    pauseControl->buttonObjects.push_back(stopButton);
    pauseControl->buttonObjects.push_back(turboButton);
    pauseControl->selectedObject = exitProjectButton;
    exitProjectButton->isSelected = true;

    exitProjectButton->buttonDown = flagButton;
    flagButton->buttonUp = exitProjectButton;

    flagButton->buttonDown = stopButton;
    stopButton->buttonUp = flagButton;

    stopButton->buttonDown = turboButton;
    turboButton->buttonUp = stopButton;

#ifdef __XBOX__
    systemButton = new ButtonObject("Exit / System", "gfx/menu/projectBox.svg", 200, 180, "gfx/menu/Ubuntu-Bold", true);
    systemButton->text->setColor(Math::color(0, 0, 0, 255));
    pauseControl->buttonObjects.push_back(systemButton);
    turboButton->buttonDown = systemButton;
    systemButton->buttonUp = turboButton;
    exitProjectButton->text->setText("Return to game list");
    pointerMoveHelp = std::make_unique<MenuText>(XboxPointerHelp::move, 200, 207);
    pointerClickHelp = std::make_unique<MenuText>(XboxPointerHelp::click, 200, 222);
    for (MenuText *line : {pointerMoveHelp.get(), pointerClickHelp.get()}) {
        line->scale = 0.65;
        line->text->setCenterAligned(true);
        line->text->setColor(Math::color(255, 255, 255, 255));
    }
#endif
    isInitialized = true;
}

void PauseMenu::finishAction(Action action) {
    if constexpr (XboxMenuTrace::enabled) XboxMenuTrace::snapshot("pause released " + std::to_string(static_cast<int>(action)));
    XboxMenuTrace::beginGameFrames();
    pendingAction = Action::None;
    if (action == Action::Exit) Scratch::shouldStop = true;
    if (action == Action::GreenFlag) Scratch::greenFlagClicked();
    if (action == Action::Stop) Scratch::stopClicked();
    shouldUnpause = true;
}

void PauseMenu::requestAction(Action action) {
#ifdef __XBOX__
    // Keep UI controls installed until confirmation is released. Otherwise A
    // becomes the game's Space key on the first frame after Green Flag/resume.
    pendingAction = action;
    if constexpr (XboxMenuTrace::enabled) XboxMenuTrace::snapshot("pause requested " + std::to_string(static_cast<int>(action)));
#else
    finishAction(action);
#endif
}

void PauseMenu::render() {
    Input::getInput();
#ifdef __XBOX__
    const bool backHeld = std::find(Input::inputButtons.begin(), Input::inputButtons.end(), "back") != Input::inputButtons.end();
    if (!backHeld) backReleased = true;
    if (pendingAction == Action::None && backReleased && backHeld) requestAction(Action::Resume);
    if (pendingAction != Action::None) {
        const auto held = [](const char *key) {
            return std::find(Input::inputKeys.begin(), Input::inputKeys.end(), key) != Input::inputKeys.end();
        };
        if (!backHeld && !held("a") && !held("x") && !held("b") && !held("y") && !Input::mousePointer.isPressed) {
            finishAction(pendingAction);
            return;
        }
    } else
#endif
    {
        pauseControl->input();
#ifdef __XBOX__
        if (systemButton->isPressed()) {
            showXboxSystemMenu();
            return;
        }
#endif

        if (backButton->isPressed({"b", "y"})) {
            requestAction(Action::Resume);
            return;
        }

        if (exitProjectButton->isPressed()) {
            requestAction(Action::Exit);
            return;
        }

        if (flagButton->isPressed()) {
            requestAction(Action::GreenFlag);
            return;
        }

        if (stopButton->isPressed()) {
            requestAction(Action::Stop);
            return;
        }

        if (turboButton->isPressed()) {
            Scratch::turbo = !Scratch::turbo;
            turboButton->text->setText(getTurboString());
            return;
        }
    }

    Render::beginFrame(0, 108, 100, 128);
    Render::beginFrame(1, 108, 100, 128);

    pauseControl->render();
    backButton->render();
#ifdef __XBOX__
    pointerMoveHelp->render();
    pointerClickHelp->render();
#endif

    Render::endFrame(false);
}

void PauseMenu::cleanup() {
    if (!isInitialized) return;
    isInitialized = false;
#ifdef __XBOX__
    Input::inputControls = std::move(gameControls);
    pointerMoveHelp.reset();
    pointerClickHelp.reset();
#endif

    if (backButton != nullptr) {
        delete backButton;
        backButton = nullptr;
    }
    if (exitProjectButton != nullptr) {
        delete exitProjectButton;
        exitProjectButton = nullptr;
    }
    if (flagButton != nullptr) {
        delete flagButton;
        flagButton = nullptr;
    }
    if (stopButton != nullptr) {
        delete stopButton;
        stopButton = nullptr;
    }
#ifdef __XBOX__
    delete systemButton;
    systemButton = nullptr;
#endif
    if (pauseControl != nullptr) {
        delete pauseControl;
        pauseControl = nullptr;
    }
    if (turboButton != nullptr) {
        delete turboButton;
        turboButton = nullptr;
    }
}

#ifdef __XBOX__
// Modal so the caller retains its selection and the paused runtime stays frozen.
void showXboxSystemMenu() {
    const auto held = [] { return !Input::inputButtons.empty() || Input::mousePointer.isPressed; };
    const auto choose = [&](const std::vector<std::string> &labels) {
        ControlObject control;
        MenuText hint("Reset Xbox: hold both triggers", 200, 190);
        MenuText hintChord("+ Back + Start for 2 seconds", 200, 205);
        for (MenuText *line : {&hint, &hintChord}) {
            line->scale = 0.65;
            line->text->setCenterAligned(true);
        }
        std::vector<std::unique_ptr<ButtonObject>> buttons;
        for (size_t i = 0; i < labels.size(); ++i) {
            buttons.emplace_back(new ButtonObject(labels[i], "gfx/menu/projectBox.svg", 200, 60 + i * 30, "gfx/menu/Ubuntu-Bold", true));
            buttons.back()->text->setColor(Math::color(0, 0, 0, 255));
            control.buttonObjects.push_back(buttons.back().get());
            if (i) {
                buttons[i-1]->buttonDown = buttons[i].get();
                buttons[i]->buttonUp = buttons[i-1].get();
            }
        }
        control.selectedObject = buttons[0].get();
        buttons[0]->isSelected = true;
        bool armed = false;
        int result = -1;
        while (Render::appShouldRun()) {
            Input::getInput();
            if (!held()) armed = true;
            if (result >= 0) {
                if (!held()) return result;
            } else if (armed) {
                control.input();
                if (Input::keyHeldDuration["b"] == 1 || Input::keyHeldDuration["y"] == 1) result = 0;
                for (size_t i = 0; i < buttons.size(); ++i)
                    if (buttons[i]->isPressed()) result = static_cast<int>(i);
            }
            Render::beginFrame(0, 108, 100, 128);
            Render::beginFrame(1, 108, 100, 128);
            control.render();
            hint.render();
            hintChord.render();
            Render::endFrame(false);
        }
        return 0;
    };
    const std::vector<std::string> labels = {"Cancel", "Return to launcher", "Restart Xbox", "Shut down Xbox"};
    int action = choose(labels);
    if (!action) return;
    if (action == 1 && !FileSystem::fileExists("E:\\Dashboard\\default.xbe")) {
        choose({"Launcher not found - return"});
        return;
    }
    if (choose({"Cancel", "Confirm: " + labels[action]}) != 1) return;
    OS::requestSystemAction(static_cast<OS::SystemAction>(action));
}
#endif
