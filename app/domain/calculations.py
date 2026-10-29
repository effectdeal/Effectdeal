from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def number(value, maximum=1000000):
    try:
        n = Decimal(str(value or 0))
        if not n.is_finite() or n < 0 or n > maximum:
            raise ValueError('Částka nebo počet je mimo povolený rozsah.')
        return n
    except (InvalidOperation, TypeError):
        raise ValueError('Zadejte platné číslo.')

def cents(value):
    return int((number(value) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def report_totals(report, rate):
    minutes = 0
    costs = 0
    for leg in report.get('legs', []):
        work = int(number(leg.get('minutes'), 1440))
        pause = int(number(leg.get('breakMinutes'), 1440))
        if pause > work:
            raise ValueError('Přestávka nemůže být delší než pracovní doba.')
        minutes += work - pause
        for key in ('tickets','fuel','parking','tolls','washing','other'):
            costs += cents(leg.get(key))
    wage = int((Decimal(minutes) * number(rate) * 100 / 60).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    bonuses = sum(cents(report.get(k)) for k in ('weekendBonus','holidayBonus','reward'))
    # Overtime is included in work minutes, not counted twice. A separate reward can be agreed.
    overtime = int(number(report.get('overtimeMinutes'), minutes))
    return {'minutes':minutes, 'overtimeMinutes':overtime, 'laborCents':wage, 'expenseCents':costs, 'bonusCents':bonuses, 'totalCents':wage+costs+bonuses}
