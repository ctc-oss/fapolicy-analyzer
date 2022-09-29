--[[
-- Copyright Concurrent Technologies Corporation 2022
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.
--]]

local REMOTE_URI = "https://github.com/ctc-oss/fapolicy-analyzer/wiki/"

local function starts_with(start, str)
  return str:sub(1, #start) == start
end

local function escape_pattern(str)
  return str:gsub("%%", "%%%%")
    :gsub("%(", "%%(")
    :gsub("%)", "%%)")
    :gsub("%.", "%%.")
    :gsub("%+", "%%+")
    :gsub("%-", "%%-")
    :gsub("%*", "%%*")
    :gsub("%?", "%%?")
    :gsub("%[", "%%[")
    :gsub("%^", "%%^")
    :gsub("%$", "%%$")
end

local function replace_start(old_val, new_val, str)
  local pattern = "^" .. old_val
  return str:gsub(pattern, new_val, 1)
end

local function make_relative_path(remote_uri, str)
  local remote_pattern = escape_pattern(remote_uri)
  return replace_start(remote_pattern, "./", str) .. ".docbook"
end

function Link(elem)
  if starts_with(REMOTE_URI, elem.target) then
    elem.target = make_relative_path(REMOTE_URI, elem.target)
    return elem
  end
end

function Image(elem)
  if starts_with(REMOTE_URI, elem.src) then
    elem.src = make_relative_path(REMOTE_URI, elem.src)
    return elem
  end
end
