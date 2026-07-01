using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Editor
{
    /// <summary>
    /// Reads cards.json from the Python prototype and generates
    /// ScriptableObject assets for every card in the game.
    /// </summary>
    public static class CardImporter
    {
        private const string AssetBasePath = "Assets/Data/Cards";
        private static readonly string DefaultJsonPath =
            Path.Combine(Application.dataPath, "../../Projects/lotr-card-game/cards.json");

        [System.Serializable]
        private class CardJson
        {
            public string cardName;
            public string faction;
            public string cardType;
            public int cost;
            public int power;
            public int toughness;
            public int defense;
            public string rarity;
            public string rulesText;
            public string flavorText;
            public List<string> creatureTypes;
            public List<string> keywords;
        }

        [System.Serializable]
        private class FactionJson
        {
            public string faction;
            public CardJson hero;
            public List<CardJson> uniqueCards;
        }

        [System.Serializable]
        private class CardManifest
        {
            public string version;
            public List<FactionJson> factions;
        }

        /// <summary>
        /// Interactive import: opens file picker.
        /// Tools > LOTR Card Game > Import Cards (File Picker)
        /// </summary>
        [MenuItem("Tools/LOTR Card Game/Import Cards (File Picker)")]
        public static void ImportAllCardsInteractive()
        {
            string jsonPath = EditorUtility.OpenFilePanel(
                "Select cards.json",
                Application.dataPath + "/../",
                "json");

            if (string.IsNullOrEmpty(jsonPath)) return;
            ImportFromPath(jsonPath);
        }

        /// <summary>
        /// Auto-import from the default prototype location.
        /// Tools > LOTR Card Game > Import Cards (Default Path)
        /// </summary>
        [MenuItem("Tools/LOTR Card Game/Import Cards (Default Path)")]
        public static void ImportFromDefaultPath()
        {
            string resolved = Path.GetFullPath(DefaultJsonPath);
            if (!File.Exists(resolved))
            {
                Debug.LogError($"cards.json not found at: {resolved}");
                return;
            }
            ImportFromPath(resolved);
        }

        /// <summary>
        /// Programmatic import from a specific path. Callable from unity_execute_code.
        /// Returns summary string: "created:N updated:N errors:N"
        /// </summary>
        public static string ImportFromPath(string jsonPath)
        {
            if (!File.Exists(jsonPath))
                return $"ERROR: File not found: {jsonPath}";

            string jsonText = File.ReadAllText(jsonPath);
            CardManifest manifest = JsonUtility.FromJson<CardManifest>(jsonText);

            if (manifest?.factions == null)
                return "ERROR: Failed to parse cards.json. Check JSON structure.";

            int created = 0;
            int updated = 0;
            int errors = 0;

            foreach (var faction in manifest.factions)
            {
                if (faction.hero != null)
                {
                    int result = CreateCardAsset(faction.hero);
                    if (result == 1) created++;
                    else if (result == 2) updated++;
                    else errors++;
                }

                if (faction.uniqueCards != null)
                {
                    foreach (var card in faction.uniqueCards)
                    {
                        int result = CreateCardAsset(card);
                        if (result == 1) created++;
                        else if (result == 2) updated++;
                        else errors++;
                    }
                }
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            string summary = $"created:{created} updated:{updated} errors:{errors}";
            Debug.Log($"Card import complete: {summary}");
            return summary;
        }

        private static int CreateCardAsset(CardJson card)
        {
            if (string.IsNullOrEmpty(card.cardName))
                return -1;

            string folder = $"{AssetBasePath}/{card.faction}";
            if (!AssetDatabase.IsValidFolder(folder))
            {
                string fullPath = Path.Combine(Application.dataPath, "..", folder);
                Directory.CreateDirectory(fullPath);
                AssetDatabase.Refresh();
            }

            string safeName = SanitizeFileName(card.cardName);
            string assetPath = $"{folder}/{safeName}.asset";

            CardData existing = AssetDatabase.LoadAssetAtPath<CardData>(assetPath);
            bool isNew = existing == null;

            CardData cardData = isNew
                ? ScriptableObject.CreateInstance<CardData>()
                : existing;

            cardData.cardName = card.cardName;
            cardData.faction = ParseEnum<Faction>(card.faction);
            cardData.cardType = ParseEnum<CardType>(card.cardType);
            cardData.rarity = ParseEnum<Rarity>(card.rarity);
            cardData.cost = card.cost;
            cardData.power = card.power;
            cardData.toughness = card.toughness;
            cardData.defense = card.defense;
            cardData.rulesText = card.rulesText ?? "";
            cardData.flavorText = card.flavorText ?? "";

            cardData.creatureTypes.Clear();
            if (card.creatureTypes != null)
                cardData.creatureTypes.AddRange(card.creatureTypes);

            cardData.keywords.Clear();
            if (card.keywords != null)
                cardData.keywords.AddRange(card.keywords);

            if (isNew)
            {
                AssetDatabase.CreateAsset(cardData, assetPath);
                return 1;
            }
            else
            {
                EditorUtility.SetDirty(cardData);
                return 2;
            }
        }

        private static T ParseEnum<T>(string value) where T : struct
        {
            if (System.Enum.TryParse<T>(value, out T result))
                return result;
            Debug.LogWarning($"Unknown enum value '{value}' for {typeof(T).Name}. Defaulting to first value.");
            return default;
        }

        private static string SanitizeFileName(string name)
        {
            foreach (char c in Path.GetInvalidFileNameChars())
                name = name.Replace(c, '_');
            return name.Replace(" ", "_");
        }
    }
}
