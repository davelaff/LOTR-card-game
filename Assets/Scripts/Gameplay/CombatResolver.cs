using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Handles combat resolution between attacker and target.
    /// Mirrors the Python engine/combat.py CombatResolver class.
    /// </summary>
    public class CombatResolver
    {
        private readonly GameManager game;

        public CombatResolver(GameManager game)
        {
            this.game = game;
        }

        /// <summary>
        /// Result of a single attack resolution.
        /// </summary>
        public class AttackResult
        {
            public int damageDealt;
            public bool targetDestroyed;
            public int trampleDamage;
            public bool locationFlipped;
            public List<string> messages = new List<string>();
        }

        /// <summary>
        /// Resolve an attack. targetType can be "ally_front", "ally_back", or "location".
        /// </summary>
        public AttackResult ResolveAttack(BoardAlly attacker, string attackerPlayer,
            object target, string targetType)
        {
            var result = new AttackResult();

            // Calculate base damage
            int damage = attacker.EffectivePower;

            // Brutal keyword: +1 damage
            if (attacker.HasKeyword("Brutal"))
                damage++;

            // Fear keyword: enemy Fear auras reduce damage
            if (targetType == "ally_front" || targetType == "ally_back")
            {
                string targetPlayer = attackerPlayer == "fp" ? "shadow" : "fp";
                int? locIndex = game.board.FindAllyLocation(attacker, attackerPlayer);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    if (loc != null)
                    {
                        foreach (var enemyAlly in loc.GetAllies(targetPlayer))
                        {
                            if (enemyAlly.HasKeyword("Fear"))
                                damage = System.Math.Max(0, damage - 1);
                        }
                    }
                }
            }

            result.damageDealt = damage;

            if (targetType == "location")
            {
                LocationSlot targetSlot = target as LocationSlot;
                string enemy = attackerPlayer == "fp" ? "shadow" : "fp";
                var enemyAlliesAtLoc = targetSlot.GetAllies(enemy);

                if (enemyAlliesAtLoc.Count == 0)
                {
                    // Undefended location — damage bypasses to Influence
                    PlayerManager enemyState = game.GetEnemyPlayer(attackerPlayer);
                    enemyState.DealInfluenceDamage(damage);
                    result.messages.Add(
                        $"{targetSlot.locationCard.cardName} is undefended! {damage} damage to " +
                        $"{(enemy == "shadow" ? "Shadow" : "Free Peoples")} Influence!");
                }
                else
                {
                    // Defended — damage goes to location defense
                    bool flipped = targetSlot.DealDefenseDamage(damage);
                    result.locationFlipped = flipped;
                    if (flipped)
                    {
                        result.messages.Add(
                            $"{targetSlot.locationCard.cardName} flips to " +
                            $"{(targetSlot.controller == "fp" ? "Free Peoples" : "Shadow")} control!");
                    }
                    else
                    {
                        result.messages.Add(
                            $"{targetSlot.locationCard.cardName} takes {damage} damage " +
                            $"(Def {targetSlot.currentDefense} remaining).");
                    }
                }
            }
            else
            {
                // Attack an ally
                BoardAlly targetAlly = target as BoardAlly;
                int excess = 0;

                // Trample calculation
                if (attacker.HasKeyword("Trample"))
                {
                    if (damage > targetAlly.currentToughness)
                        excess = damage - targetAlly.currentToughness;
                }

                // Apply damage
                targetAlly.TakeDamage(damage);
                result.messages.Add(
                    $"{targetAlly.card.cardName} takes {damage} damage " +
                    $"(Toughness: {targetAlly.currentToughness}/{targetAlly.card.toughness}).");

                // Check destruction
                if (targetAlly.currentToughness <= 0)
                {
                    result.targetDestroyed = true;
                    result.messages.Add($"{targetAlly.card.cardName} is destroyed!");

                    // Ring-bearer killed?
                    if (attackerPlayer == "shadow" &&
                        game.fpPlayer.hero != null && targetAlly == game.fpPlayer.hero)
                    {
                        result.messages.Add("*** THE RING IS SEIZED BY THE SHADOW! ***");
                    }
                    else if (attackerPlayer == "fp" &&
                             game.shadowPlayer.hero != null && targetAlly == game.shadowPlayer.hero)
                    {
                        if (game.ring.bearer == "shadow")
                            result.messages.Add("*** THE RING IS RECOVERED BY THE FREE PEOPLES! ***");
                    }
                }

                // Resolve on-destroy effects
                string destroyedPlayer = attackerPlayer == "fp" ? "shadow" : "fp";
                var destroyMsgs = game.effects.ResolveOnDestroy(targetAlly, destroyedPlayer);
                result.messages.AddRange(destroyMsgs);

                // Handle trample damage to Influence
                if (excess > 0)
                {
                    result.trampleDamage = excess;
                    PlayerManager targetPlayerState = game.GetEnemyPlayer(attackerPlayer);
                    targetPlayerState.DealInfluenceDamage(excess);
                    result.messages.Add($"Trample: {excess} excess damage to Influence!");
                }
            }

            // Attacker becomes tapped
            attacker.tapped = true;
            attacker.hasAttackedThisTurn = true;

            return result;
        }
    }
}
