local http = require("http");
local data = require("data");

local auth = string.format('Basic %s', data.tobase64(string.format("%s:%s", settings.login, settings.password)));


--@help set_label
set_label = function(state)
    layout.current_state.text = string.format("Current state: %s", state.id);
    layout.current_state.color = state.color;
end

--@help get_url
get_url = function(url)
    return string.format('%s%s', settings.url, url)
end

--@help get_info
get_info = function ()
    local headers = { Authorization = auth };
    local req = { method = "get",
                  url = get_url('/info'),
                  mime = "text/json",
                  headers = headers };
    http.request(req, function (err, resp)
        if (err) then return; end
        local data = data.fromjson(resp.content);
        set_label(data.current_state);
        for state_id, state in pairs(data.states) do
            state_button = layout[string.format("state_%s", state_id)];
            state_button.text = state.id;
            state_button.color = state.color;
        end
        layout.info.text = string.format("AlarMe v%s", data.app.version);
    end);
end

--@help set_state
set_state = function(state)
    local headers = { Authorization = auth, ["Content-Type"] = "application/x-www-form-urlencoded" };
    local req = { method = "post",
                  url = get_url('/control'),
                  mime = "text/plain",
                  headers = headers,
                  content = string.format("behaviour=%s", state) };
    http.request(req, function (err, resp)
        if (err) then return; end
        get_info();
    end);
end

--@help set_state_start
actions.set_state_start = function()
    set_state("start");
end

--@help set_state_disable
actions.set_state_disable = function()
    set_state("disable");
end

--@help set_state_pass
actions.set_state_pass= function()
    set_state("pass");
end

--@help set_state_stay
actions.set_state_stay = function()
    set_state("stay");
end

--@help set_state_guard
actions.set_state_guard = function()
    set_state("guard");
end

--@help set_state_alarm
actions.set_state_alarm = function()
    set_state("alarm");
end

--@help reload
actions.reload = function()
    get_info();
end

events.create = get_info;
events.focus = get_info;
