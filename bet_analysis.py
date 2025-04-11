import sqlite3

def get_bet_results():
    conn = sqlite3.connect("bet_sort.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.id AS bet_id, 
               b.heading, 
               b.optionid AS winner_option_id, 
               bo.id AS option_id, 
               bo.text, 
               bo.odds, 
               bo.bonus_total
        FROM bets b
        JOIN bet_options bo ON b.id = bo.gameid
        ORDER BY b.id ASC, bo.id ASC;
    """)
    bets = cursor.fetchall()

    results = {}
    for bet_id, heading, winner_option_id, option_id, option_text, odds, bonus_total in bets:
        if bet_id not in results:
            results[bet_id] = {
                "bet_id": bet_id,
                "heading": heading,
                "winner_option_id": winner_option_id,
                "options": []
            }
        
        results[bet_id]["options"].append({
            "option_id": option_id,
            "option_text": option_text,
            "odds": odds,
            "bonus_total": bonus_total,
            "is_winner": (option_id == winner_option_id)
        })

    conn.close()
    return results

if __name__ == "__main__":
    bet_results = get_bet_results()
    
    if not bet_results:
        print("No results found.")
    else:
        for bet in bet_results.values():
            print(f"🏆 Bet {bet['bet_id']}: {bet['heading']}")
            for option in bet["options"]:
                status = "✅ Winner" if option["is_winner"] else "❌"
                print(f"  {status} Option {option['option_id']}: {option['option_text']} (Odds: {option['odds']}, Bonus: {option['bonus_total']})")
            print()
