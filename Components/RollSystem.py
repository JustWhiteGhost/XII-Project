class RollingSystem:
    
    @staticmethod
    def _resolve_check(roll: int, total_mod: int, target: int) -> dict:
        """
        Helper function: Merges the logic for d20Roll, SaveRoll, CriticalRoll, and PersuadeRoll.
        Calculates the total and standard success/crit states.
        """
        total = roll + total_mod
        return {
            "roll": roll,
            "total": total,
            "success": total >= target,
            "is_nat20": roll == 20,
            "is_nat1": roll == 1
        }

    @staticmethod
    def d20RollCheck(roll: int, mod: int, bonus: int = 0, AC: int = 10) -> dict:
        # MERGED: Uses _resolve_check
        res = RollingSystem._resolve_check(roll, mod + bonus, AC)
        return {
            "roll": res["roll"], 
            "total": res["total"], 
            "hit": res["success"], 
            "critical": res["is_nat20"], 
            "fumble": res["is_nat1"]
        }

    @staticmethod
    def SaveRoll(roll: int, ag_mod: int, dex_mod: int, DC: int) -> dict:
        # MERGED: Uses _resolve_check
        res = RollingSystem._resolve_check(roll, ag_mod + dex_mod, DC)
        # Added 'success' because your original code calculated total but didn't say if you passed!
        return {
            "roll": res["roll"], 
            "total": res["total"], 
            "success": res["success"],
            "complete_negate": res["is_nat20"], 
            "perfect_fail": res["is_nat1"]
        }

    @staticmethod
    def CricticalRoll(roll: int, crit_mod: int, DC: int) -> dict:
        # MERGED: Uses _resolve_check
        res = RollingSystem._resolve_check(roll, crit_mod, DC)
        return {
            "roll": res["roll"], 
            "total": res["total"], 
            "critical_success": res["success"], 
            "critical_fail": res["is_nat1"]
        }

    @staticmethod
    def PersuadeRoll(roll: int, cha_mod: int, wis_mod: int, relation_mod: int, DC: int) -> dict:
        # MERGED: Uses _resolve_check
        res = RollingSystem._resolve_check(roll, cha_mod + wis_mod + relation_mod, DC)
        return {
            "roll": res["roll"], 
            "total": res["total"], 
            "success": res["success"]
        }

    @staticmethod
    def ContestRoll(UserRoll: int, OpponentRoll: int, UserMod: int = 0, OpponentMod: int = 0) -> dict:
        """Perform a contest roll between user and opponent"""
        user_total = UserRoll + UserMod
        opponent_total = OpponentRoll + OpponentMod
        
        if user_total > opponent_total:
            winner = 1
        elif opponent_total > user_total:
            winner = -1
        else:
            winner = 0
            
        return {
            "user_roll": UserRoll, "user_total": user_total,
            "opponent_roll": OpponentRoll, "opponent_total": opponent_total,
            "winner": winner
        }

    @staticmethod
    def DamageRoll(rolls: list[int], Str_Damage: int, Weapon_dmg: int, modifier: int = 0, bonus: int = 0) -> dict:
        """Calculate damage from a list of rolls and a modifier"""
        total_damage = sum(rolls) + Str_Damage + Weapon_dmg + modifier + bonus
        return {"rolls": rolls, "modifier": modifier, "total_damage": total_damage}

    @staticmethod
    def BargainRoll(roll: int, cha_mod: int, int_mod: int, relation_mod: int, DC: int) -> dict:
        """Perform a bargain roll against a DC"""
        total = roll + cha_mod + int_mod + relation_mod
        margin = total - DC

        discount = 0
        status = "No Deal"

        # FIXED LOGIC: Changed order so negative values are actually caught correctly
        if margin >= 10:
            discount = 30
            status = "Excellent Deal"
        elif margin >= 5:
            discount = 20
            status = "Good Deal"
        elif margin >= 0:
            discount = 10
            status = "Fair Deal"
        # Removed 'elif margin == 0' because '>= 0' above already catches it.
        elif margin <= -5:  # Check the extreme negative first!
            discount = -20
            status = "Bad Deal"
        elif margin < 0:    # Then check the general negative
            discount = -10
            status = "Poor Deal"
            
        return {"roll": roll, "total": total, "discount": discount, "status": status}