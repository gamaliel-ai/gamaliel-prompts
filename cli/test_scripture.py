"""
Tests for the scripture module.
"""

import pytest
from unittest.mock import Mock, patch
from .scripture import BSBParser, get_bsb_parser


class TestBSBParser:
    """Test cases for BSBParser class."""
    
    def test_init(self):
        """Test parser initialization."""
        parser = BSBParser()
        assert parser.url == "https://bereanbible.com/bsb.txt"
        assert parser.verses == {}
        assert parser.chapters == {}
        assert parser._loaded is False
    
    def test_normalize_book_name(self):
        """Test book name normalization."""
        parser = BSBParser()
        
        # Test common abbreviations
        assert parser._normalize_book_name("gen") == "Genesis"
        assert parser._normalize_book_name("exo") == "Exodus"
        assert parser._normalize_book_name("mat") == "Matthew"
        assert parser._normalize_book_name("jhn") == "John"
        assert parser._normalize_book_name("rev") == "Revelation"
        
        # Test full names
        assert parser._normalize_book_name("Genesis") == "Genesis"
        assert parser._normalize_book_name("John") == "John"
        
        # Test unknown names
        assert parser._normalize_book_name("Unknown") == "Unknown"
    
    @patch('requests.get')
    def test_download_and_parse_success(self, mock_get):
        """Test successful download and parsing."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = """[Genesis 1]
1 In the beginning God created the heavens and the earth.
2 The earth was formless and void, and darkness was over the surface of the deep.
[Genesis 2]
1 Thus the heavens and the earth were completed, and all their hosts.
2 By the seventh day God completed His work which He had done."""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = BSBParser()
        result = parser.download_and_parse()
        
        assert result is True
        assert parser._loaded is True
        assert "Genesis" in parser.verses
        assert 1 in parser.verses["Genesis"]
        assert 2 in parser.verses["Genesis"]
        assert 1 in parser.verses["Genesis"][1]
        assert 2 in parser.verses["Genesis"][1]
        assert "In the beginning God created" in parser.verses["Genesis"][1][1]
    
    @patch('requests.get')
    def test_download_and_parse_failure(self, mock_get):
        """Test download failure handling."""
        # Mock failed request
        mock_get.side_effect = Exception("Network error")
        
        parser = BSBParser()
        result = parser.download_and_parse()
        
        assert result is False
        assert parser._loaded is False
    
    def test_get_verse_not_loaded(self):
        """Test getting verse when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.get_verse("Genesis", 1, 1)
            mock_download.assert_called_once()
    
    def test_get_chapter_not_loaded(self):
        """Test getting chapter when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.get_chapter("Genesis", 1)
            mock_download.assert_called_once()
    
    def test_list_books_not_loaded(self):
        """Test listing books when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.list_books()
            mock_download.assert_called_once()
    
    def test_search_text_not_loaded(self):
        """Test text search when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.search_text("God")
            mock_download.assert_called_once()


class TestBSBParserIntegration:
    """Integration tests for BSBParser."""
    
    @patch('requests.get')
    def test_full_parsing_workflow(self, mock_get):
        """Test the complete parsing workflow."""
        # Mock BSB text with multiple books and chapters
        mock_response = Mock()
        mock_response.text = """[Genesis 1]
1 In the beginning God created the heavens and the earth.
2 The earth was formless and void.
[Genesis 2]
1 Thus the heavens and the earth were completed.
[Exodus 1]
1 Now these are the names of the sons of Israel."""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = BSBParser()
        success = parser.download_and_parse()
        
        assert success is True
        assert "Genesis" in parser.verses
        assert "Exodus" in parser.verses
        assert len(parser.verses["Genesis"]) == 2
        assert len(parser.verses["Exodus"]) == 1
        
        # Test verse retrieval
        verse = parser.get_verse("Genesis", 1, 1)
        assert verse == "In the beginning God created the heavens and the earth."
        
        # Test chapter retrieval
        chapter = parser.get_chapter("Genesis", 1)
        assert "In the beginning God created" in chapter
        
        # Test book listing
        books = parser.list_books()
        assert "Genesis" in books
        assert "Exodus" in books
        
        # Test text search
        results = parser.search_text("God")
        assert len(results) > 0
        assert any("God" in result[3] for result in results)


class TestGlobalFunctions:
    """Test cases for global functions."""
    
    def test_get_bsb_parser_singleton(self):
        """Test that get_bsb_parser returns a singleton instance."""
        parser1 = get_bsb_parser()
        parser2 = get_bsb_parser()
        assert parser1 is parser2
        assert isinstance(parser1, BSBParser)


if __name__ == "__main__":
    pytest.main([__file__])
