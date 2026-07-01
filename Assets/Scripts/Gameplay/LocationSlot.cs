using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// A single location slot on the board (0, 1, or 2).
    /// Holds the location card, defense, controller, and ally lines per player.
    /// </summary>
    [System.Serializable]
    public class LocationSlot
    {
        public int index;
        public CardData locationCard;
        public int currentDefense;
        public string controller; // "fp", "shadow", or null

        public int fortifyBonus;

        public List<BoardAlly> fpFront = new List<BoardAlly>();
        public List<BoardAlly> fpBack = new List<BoardAlly>();
        public List<BoardAlly> shadowFront = new List<BoardAlly>();
        public List<BoardAlly> shadowBack = new List<BoardAlly>();

        // --- Queries ---

        public bool IsEmpty => locationCard == null;

        public bool IsControlledBy(string player) => controller == player;

        public bool IsContested =>
            (fpFront.Count + fpBack.Count) > 0 && (shadowFront.Count + shadowBack.Count) > 0;

        public List<BoardAlly> GetAllies(string player)
        {
            if (player == "fp")
                return ConcatLists(fpFront, fpBack);
            return ConcatLists(shadowFront, shadowBack);
        }

        public List<BoardAlly> GetFrontLine(string player)
        {
            return player == "fp" ? fpFront : shadowFront;
        }

        public List<BoardAlly> GetBackLine(string player)
        {
            return player == "fp" ? fpBack : shadowBack;
        }

        public bool HasFrontLine(string player)
        {
            return GetFrontLine(player).Count > 0;
        }

        // --- Mutations ---

        /// <summary>
        /// Add an ally to a row. Returns false if row is full.
        /// </summary>
        public bool AddAlly(BoardAlly ally, string player, string row = "front")
        {
            List<BoardAlly> target = row == "front" ? GetFrontLine(player) : GetBackLine(player);
            if (target.Count >= BoardManager.MaxRowCapacity)
                return false;
            target.Add(ally);
            return true;
        }

        /// <summary>
        /// Remove an ally from any row at this location. Returns true if found.
        /// </summary>
        public bool RemoveAlly(BoardAlly ally, string player)
        {
            foreach (var lst in new[] { GetFrontLine(player), GetBackLine(player) })
            {
                for (int i = 0; i < lst.Count; i++)
                {
                    if (lst[i] == ally)
                    {
                        lst.RemoveAt(i);
                        return true;
                    }
                }
            }
            return false;
        }

        /// <summary>
        /// Find which row an ally is in. Returns "front", "back", or null.
        /// </summary>
        public string FindAllyRow(BoardAlly ally, string player)
        {
            if (GetFrontLine(player).Contains(ally))
                return "front";
            if (GetBackLine(player).Contains(ally))
                return "back";
            return null;
        }

        /// <summary>
        /// Deal damage to location defense. Returns true if location flips.
        /// </summary>
        public bool DealDefenseDamage(int amount)
        {
            currentDefense -= amount;
            if (currentDefense <= 0)
            {
                string oldController = controller;
                controller = oldController == "fp" ? "shadow" : "fp";
                currentDefense = (locationCard != null ? locationCard.defense : 0) + fortifyBonus;
                return true;
            }
            return false;
        }

        // --- Helpers ---

        private static List<BoardAlly> ConcatLists(List<BoardAlly> a, List<BoardAlly> b)
        {
            var result = new List<BoardAlly>(a.Count + b.Count);
            result.AddRange(a);
            result.AddRange(b);
            return result;
        }
    }
}
