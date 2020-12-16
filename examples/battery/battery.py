from pitop.battery import Battery


battery = Battery()

print(f"Battery capacity: {battery.capacity}")
print(f"Battery time remaining: {battery.time_remaining}")
print(f"Battery is charging: {battery.is_charging}")
print(f"Battery is full: {battery.is_full}")
print(f"Battery wattage: {battery.wattage}")


def do_low_battery_thing():
    print("Battery is low!")


def do_critical_battery_thing():
    print("Battery is critically low!")


def do_full_battery_thing():
    print("Battery is full!")


def do_charging_battery_thing():
    print("Battery is charging!")


def do_discharging_battery_thing():
    print("Battery is discharging!")


# To invoke a function when the battery changes state, you can assign the function to various 'when_' data members
battery.when_low = do_low_battery_thing
battery.when_critical = do_critical_battery_thing
battery.when_full = do_full_battery_thing
battery.when_charging = do_charging_battery_thing
battery.when_discharging = do_discharging_battery_thing


# Another way to react to battery events is to poll
while True:
    if battery.is_full:
        do_full_battery_thing()
